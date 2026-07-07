"""
api.py
------
Phase 4: Production — exposes the chatbot as a REST API using FastAPI.

Run with:
    uvicorn api:app --reload --port 8000

Then send requests to http://localhost:8000/chat (see README for examples).

Each caller supplies a `session_id` so multiple people (or apps) can talk to
the bot at the same time, each with their own conversation history — the
same conversation memory built in Phase 2, just usable over HTTP now instead
of only in the terminal.
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from document_loader import load_documents
from retriever import search
from responder import generate_response_with_meta
from config import USE_VECTOR_SEARCH
from analytics import analytics
from feedback import feedback_store

logger = logging.getLogger(__name__)

# --------------------------------------------------
# Performance: simple response cache (Phase 4)
# --------------------------------------------------
# Caches answers for the FIRST question of a fresh conversation (no history
# yet), since those are the most likely to repeat across different users
# (e.g. many people asking "What is your return policy?"). Once a
# conversation has history, we don't cache — the answer may legitimately
# depend on what was said before, and caching it could return a stale or
# wrong answer.
_response_cache: Dict[str, str] = {}
MAX_CACHE_SIZE = 500

# --------------------------------------------------
# Semantic search with automatic TF-IDF fallback
# (same logic as chatbot.py, reused here for the API)
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
    retrieval understands short follow-ups that only make sense in light
    of what was just discussed. Only affects retrieval, not the prompt
    shown to the LLM (which still sees the original question).
    """
    if not history:
        return query
    previous_user_messages = [turn["content"] for turn in history if turn["role"] == "user"]
    if not previous_user_messages:
        return query
    return f"{previous_user_messages[-1]} {query}"


# --------------------------------------------------
# In-memory conversation history, per session
# --------------------------------------------------
# NOTE: this resets whenever the API server restarts. For a real production
# deployment, this would be swapped for a database or Redis — that's a good
# next step to mention in an interview, but out of scope for this playbook.
_sessions: Dict[str, List[Dict]] = {}

MAX_SESSIONS = 1000  # simple safety limit so memory usage can't grow forever


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
    version="0.3.0",
)

_document_count = 0


@app.on_event("startup")
def on_startup():
    global _document_count
    documents = load_documents()
    _document_count = len(documents)
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
    Conversation history is tracked per session_id automatically.

    The response includes a response_id — submit it to POST /feedback to
    tell us whether that particular answer was helpful.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")

    start_time = time.perf_counter()
    history = _sessions.get(request.session_id, [])

    # Performance optimization: reuse a cached answer for repeated first
    # questions (no conversation history yet) instead of re-running search
    # + LLM generation every time.
    cache_key = request.message.strip().lower()
    if not history and cache_key in _response_cache:
        response_text = _response_cache[cache_key]
        used_ai = False  # served from cache, no fresh generation happened
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

    history.append({"role": "user", "content": request.message})
    history.append({"role": "assistant", "content": response_text})

    if request.session_id not in _sessions and len(_sessions) >= MAX_SESSIONS:
        # Very simple eviction: drop an arbitrary old session rather than growing forever.
        _sessions.pop(next(iter(_sessions)))

    _sessions[request.session_id] = history

    duration_ms = (time.perf_counter() - start_time) * 1000
    analytics.record(request.message, duration_ms, used_ai, result_count)

    response_id = feedback_store.register_response(request.message, response_text)

    return ChatResponse(response=response_text, session_id=request.session_id, response_id=response_id)


@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    """
    Rate a previous response as helpful or not. Use the response_id
    returned by POST /chat.
    """
    if request.rating not in ("positive", "negative"):
        raise HTTPException(status_code=400, detail='rating must be "positive" or "negative"')

    success = feedback_store.record_feedback(request.response_id, request.rating, request.comment)
    if not success:
        raise HTTPException(status_code=404, detail="response_id not found (it may have expired)")

    return {"status": "recorded"}


@app.delete("/chat/{session_id}")
def reset_session(session_id: str):
    """Clear the conversation history for a given session."""
    _sessions.pop(session_id, None)
    return {"status": "cleared", "session_id": session_id}