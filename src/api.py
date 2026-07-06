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
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from document_loader import load_documents
from retriever import search
from responder import generate_response
from config import USE_VECTOR_SEARCH

logger = logging.getLogger(__name__)

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


class HealthResponse(BaseModel):
    status: str
    documents_loaded: int
    vector_search_enabled: bool


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


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Send a customer question, get back an AI-generated (or template) answer.
    Conversation history is tracked per session_id automatically.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")

    history = _sessions.get(request.session_id, [])

    search_query = build_search_query(request.message, history)
    search_results = run_search(search_query)
    response_text = generate_response(search_results, request.message, history)

    history.append({"role": "user", "content": request.message})
    history.append({"role": "assistant", "content": response_text})

    if request.session_id not in _sessions and len(_sessions) >= MAX_SESSIONS:
        # Very simple eviction: drop an arbitrary old session rather than growing forever.
        _sessions.pop(next(iter(_sessions)))

    _sessions[request.session_id] = history

    return ChatResponse(response=response_text, session_id=request.session_id)


@app.delete("/chat/{session_id}")
def reset_session(session_id: str):
    """Clear the conversation history for a given session."""
    _sessions.pop(session_id, None)
    return {"status": "cleared", "session_id": session_id}