"""
api.py
------
Production API for the AI Customer Support Playbook — FastAPI-based, with
chat, dashboard, feedback, and admin (including knowledge base management)
routes.

Run with:
    uvicorn api:app --reload --port 8000

Conversation history is persisted in a SQLite database (database.py), so it
survives server restarts. The knowledge base itself can be replaced entirely
per client via the admin panel's upload feature — see /admin/knowledge-base
routes below. Combined with COMPANY_NAME / BUSINESS_TYPE in .env, this same
codebase can be deployed for any business, not just the original demo.
"""

import logging
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Header, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel

from document_loader import load_documents
from retriever import search
from responder import generate_response_with_meta
from config import USE_VECTOR_SEARCH, ADMIN_TOKEN, KNOWLEDGE_BASE_DIR
from analytics import analytics
from feedback import feedback_store
import database

logger = logging.getLogger(__name__)

# --------------------------------------------------
# Semantic search with automatic TF-IDF fallback
# --------------------------------------------------
_semantic_search = None
_rebuild_index = None
if USE_VECTOR_SEARCH:
    try:
        from embeddings import semantic_search as _semantic_search
        from embeddings import rebuild_index as _rebuild_index
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
    """Enrich the search query with the customer's previous question, for context-aware retrieval."""
    if not history:
        return query
    previous_user_messages = [turn["content"] for turn in history if turn["role"] == "user"]
    if not previous_user_messages:
        return query
    return f"{previous_user_messages[-1]} {query}"


# --------------------------------------------------
# Performance: simple response cache
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
    response_id: str


class FeedbackRequest(BaseModel):
    response_id: str
    rating: str
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
    description="Configurable RAG-based customer support API — swap the knowledge base to deploy for any business.",
    version="1.1.0",
)

_document_count = 0


def _refresh_document_count():
    global _document_count
    _document_count = len(load_documents())
    return _document_count


@app.on_event("startup")
def on_startup():
    _refresh_document_count()
    database.init_db()
    logger.info(f"API started, {_document_count} knowledge base document(s) loaded")


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        documents_loaded=_document_count,
        vector_search_enabled=_semantic_search is not None,
    )


@app.get("/chat-ui")
def chat_ui():
    """Simple browser-based chat interface — talk to the bot without curl or code."""
    return FileResponse(Path(__file__).parent / "static" / "chat.html", media_type="text/html")


@app.get("/dashboard")
def dashboard():
    """Visual analytics dashboard (auto-refreshing) — reads live data from /stats."""
    return FileResponse(Path(__file__).parent / "static" / "dashboard.html", media_type="text/html")


@app.get("/stats", response_model=StatsResponse)
def stats():
    summary = analytics.summary()
    summary["feedback"] = feedback_store.summary()
    return summary


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")

    start_time = time.perf_counter()
    history = database.get_history(request.session_id)

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
    database.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}


@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    if request.rating not in ("positive", "negative"):
        raise HTTPException(status_code=400, detail='rating must be "positive" or "negative"')
    success = feedback_store.record_feedback(request.response_id, request.rating, request.comment)
    if not success:
        raise HTTPException(status_code=404, detail="response_id not found (it may have expired)")
    return {"status": "recorded"}


# --------------------------------------------------
# Admin interface
# --------------------------------------------------
def _check_admin_token(x_admin_token: Optional[str]) -> None:
    """
    Simple shared-secret protection — adequate for a portfolio/small-business
    deployment, not a substitute for real per-user authentication.
    """
    if not ADMIN_TOKEN:
        logger.warning("ADMIN_TOKEN not set — admin endpoints are unprotected.")
        return
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing admin token")


@app.get("/admin")
def admin_page():
    return FileResponse(Path(__file__).parent / "static" / "admin.html", media_type="text/html")


@app.get("/admin/sessions")
def admin_list_sessions(x_admin_token: Optional[str] = Header(None)):
    _check_admin_token(x_admin_token)
    return {"sessions": database.list_sessions()}


@app.get("/admin/sessions/{session_id}")
def admin_get_session(session_id: str, x_admin_token: Optional[str] = Header(None)):
    _check_admin_token(x_admin_token)
    history = database.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found or empty")
    return {"session_id": session_id, "messages": history}


@app.delete("/admin/sessions/{session_id}")
def admin_delete_session(session_id: str, x_admin_token: Optional[str] = Header(None)):
    _check_admin_token(x_admin_token)
    database.clear_session(session_id)
    return {"status": "deleted", "session_id": session_id}


def _reindex_after_kb_change() -> Optional[int]:
    """Refresh document count and rebuild the vector index after a knowledge base change."""
    _refresh_document_count()
    if _rebuild_index is None:
        return None
    try:
        return _rebuild_index()
    except Exception as exc:
        logger.error(f"Failed to rebuild vector index: {exc}")
        return None


@app.get("/admin/knowledge-base")
def admin_list_kb_files(x_admin_token: Optional[str] = Header(None)):
    """List every file currently in the knowledge base."""
    _check_admin_token(x_admin_token)
    files = sorted(p.name for p in Path(KNOWLEDGE_BASE_DIR).glob("*.md")) + \
            sorted(p.name for p in Path(KNOWLEDGE_BASE_DIR).glob("*.txt"))
    return {"files": files, "documents_loaded": _document_count}


@app.post("/admin/knowledge-base/upload")
async def admin_upload_kb_file(file: UploadFile = File(...), x_admin_token: Optional[str] = Header(None)):
    """
    Upload a .md or .txt file into the knowledge base. Replaces a file of
    the same name if it already exists. Automatically rebuilds the vector
    search index so the new content is searchable immediately.
    """
    _check_admin_token(x_admin_token)

    if not file.filename.endswith((".md", ".txt")):
        raise HTTPException(status_code=400, detail="Only .md or .txt files are supported")

    Path(KNOWLEDGE_BASE_DIR).mkdir(parents=True, exist_ok=True)
    dest = Path(KNOWLEDGE_BASE_DIR) / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    chunks_indexed = _reindex_after_kb_change()
    logger.info(f"Knowledge base file uploaded: {file.filename}")

    return {
        "status": "uploaded",
        "filename": file.filename,
        "documents_loaded": _document_count,
        "vector_chunks_indexed": chunks_indexed,
    }


@app.delete("/admin/knowledge-base/{filename}")
def admin_delete_kb_file(filename: str, x_admin_token: Optional[str] = Header(None)):
    """Remove a file from the knowledge base and rebuild the search index."""
    _check_admin_token(x_admin_token)

    path = Path(KNOWLEDGE_BASE_DIR) / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    path.unlink()

    chunks_indexed = _reindex_after_kb_change()
    logger.info(f"Knowledge base file deleted: {filename}")

    return {
        "status": "deleted",
        "filename": filename,
        "documents_loaded": _document_count,
        "vector_chunks_indexed": chunks_indexed,
    }