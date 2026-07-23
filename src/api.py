"""
api.py
------
Phase 4/5: Production — exposes the chatbot as a REST API using FastAPI.

Run with:
    uvicorn api:app --reload --port 8000

Conversation history is now persisted in a SQLite database (database.py),
so it survives server restarts — previously it lived only in memory.
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel

from document_loader import load_documents
from retriever import search
from responder import generate_response_with_meta
from config import USE_VECTOR_SEARCH, ADMIN_TOKEN
from analytics import analytics
from feedback import feedback_store
import database

logger = logging.getLogger(__name__)

# --------------------------------------------------
# Semantic search with automatic TF-IDF fallback
# --------------------------------------------------
_semantic_search = None
if USE_VECTOR_SEARCH:
    try:
        from embeddings import semantic_search as _semantic_search
    except Exception as exc:
        logger.warning(f"Vector search unavailable, falling back to TF-IDF: {exc}")


def run_search(query: str):
    if _semantic_search is not None:
        try:
            return _semantic_search(query)
        except Exception as exc:
            logger.error(f"Semantic search failed, falling back to TF-IDF: {exc}")
    return search(query)


def build_search_query(query: str, history: List[Dict]) -> str:
    """
    Enrich the search query with the customer's previous question, so
    retrieval understands short follow-ups. Only affects retrieval, not
    the prompt shown to the LLM (which still sees the original question).
    """
    if not history:
        return query
    previous_user_messages = [turn["content"] for turn in history if turn["role"] == "user"]
    if not previous_user_messages:
        return query
    return f"{previous_user_messages[-1]} {query}"


# --------------------------------------------------
# Performance: simple response cache (Phase 4)
# --------------------------------------------------
_response_cache: Dict[str, str] = {}
MAX_CACHE_SIZE = 500


# --------------------------------------------------
# Request / response schemas
# --------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str
    response_id: str  # use this to submit feedback via POST /feedback


class FeedbackRequest(BaseModel):
    response_id: str
    rating: str  # "positive" or "negative"
    comment: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    documents_loaded: int
    vector_search_enabled: bool


class StatsResponse(BaseModel):
    total_requests: int
    avg_response_time_ms: float
    ai_generation_used: int
    template_fallback_used: int
    ai_generation_rate_pct: float
    no_relevant_results_rate_pct: float
    recent_queries: List[Dict]
    feedback: Dict


# --------------------------------------------------
# App setup
# --------------------------------------------------
app = FastAPI(
    title="AI Customer Support Playbook API",
    description="REST API for the RAG-based customer support chatbot.",
    version="0.5.0",
)

_document_count = 0


@app.on_event("startup")
def on_startup():
    global _document_count
    documents = load_documents()
    _document_count = len(documents)
    database.init_db()
    logger.info(f"API started, {_document_count} knowledge base document(s) loaded")


@app.get("/health", response_model=HealthResponse)
def health():
    """Simple health check — confirms the API is up and the knowledge base loaded."""
    return HealthResponse(
        status="ok",
        documents_loaded=_document_count,
        vector_search_enabled=_semantic_search is not None,
    )


@app.get("/dashboard")
def dashboard():
    """Visual analytics dashboard (auto-refreshing) — reads live data from /stats."""
    dashboard_path = Path(__file__).parent / "static" / "dashboard.html"
    return FileResponse(dashboard_path, media_type="text/html")


@app.get("/stats", response_model=StatsResponse)
def stats():
    """Basic usage monitoring: request volume, response times, AI usage rate, and user feedback."""
    summary = analytics.summary()
    summary["feedback"] = feedback_store.summary()
    return summary


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Send a customer question, get back an AI-generated (or template) answer.
    Conversation history is persisted per session_id in a SQLite database,
    so it survives server restarts.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")

    start_time = time.perf_counter()
    history = database.get_history(request.session_id)

    # Performance optimization: reuse a cached answer for repeated first
    # questions (no conversation history yet) instead of re-running search
    # + LLM generation every time.
    cache_key = request.message.strip().lower()
    if not history and cache_key in _response_cache:
        response_text = _response_cache[cache_key]
        used_ai = False
        result_count = 1
    else:
        search_query = build_search_query(request.message, history)
        search_results = run_search(search_query)
        response_text, used_ai = generate_response_with_meta(search_results, request.message, history)
        result_count = len(search_results)

        if not history:
            if len(_response_cache) >= MAX_CACHE_SIZE:
                _response_cache.pop(next(iter(_response_cache)))
            _response_cache[cache_key] = response_text

    database.save_message(request.session_id, "user", request.message)
    database.save_message(request.session_id, "assistant", response_text)

    duration_ms = (time.perf_counter() - start_time) * 1000
    analytics.record(request.message, duration_ms, used_ai, result_count)

    response_id = feedback_store.register_response(request.message, response_text)

    return ChatResponse(response=response_text, session_id=request.session_id, response_id=response_id)


@app.delete("/chat/{session_id}")
def reset_session(session_id: str):
    """Permanently delete the conversation history for a given session."""
    database.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}


@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    """Rate a previous response as helpful or not. Use the response_id returned by POST /chat."""
    if request.rating not in ("positive", "negative"):
        raise HTTPException(status_code=400, detail='rating must be "positive" or "negative"')

    success = feedback_store.record_feedback(request.response_id, request.rating, request.comment)
    if not success:
        raise HTTPException(status_code=404, detail="response_id not found (it may have expired)")

    return {"status": "recorded"}


# --------------------------------------------------
# Admin interface (Phase 5)
# --------------------------------------------------
def _check_admin_token(x_admin_token: Optional[str]) -> None:
    """
    Very simple shared-secret protection for admin endpoints — enough for
    a portfolio project, not a substitute for real auth in production
    (that would mean per-user accounts, hashed credentials, and HTTPS-only
    cookies/JWTs instead of a single static token).
    """
    if not ADMIN_TOKEN:
        # No token configured: admin endpoints are open. Fine for local
        # development, but a warning is logged so it isn't accidentally
        # left this way in a real deployment.
        logger.warning("ADMIN_TOKEN not set — admin endpoints are unprotected.")
        return
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing admin token")


@app.get("/admin")
def admin_page():
    """Serves the admin panel UI (session browser)."""
    admin_path = Path(__file__).parent / "static" / "admin.html"
    return FileResponse(admin_path, media_type="text/html")


@app.get("/admin/sessions")
def admin_list_sessions(x_admin_token: Optional[str] = Header(None)):
    """List every conversation session stored in the database."""
    _check_admin_token(x_admin_token)
    return {"sessions": database.list_sessions()}


@app.get("/admin/sessions/{session_id}")
def admin_get_session(session_id: str, x_admin_token: Optional[str] = Header(None)):
    """Full message history for one session."""
    _check_admin_token(x_admin_token)
    history = database.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found or empty")
    return {"session_id": session_id, "messages": history}


@app.delete("/admin/sessions/{session_id}")
def admin_delete_session(session_id: str, x_admin_token: Optional[str] = Header(None)):
    """Permanently delete a conversation from the database."""
    _check_admin_token(x_admin_token)
    database.clear_session(session_id)
    return {"status": "deleted", "session_id": session_id}