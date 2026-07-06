"""
config.py
---------
Central configuration settings for the AI Customer Support Playbook.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --------------------------------------------------
# Project Info
# --------------------------------------------------
PROJECT_NAME = "AI Customer Support Playbook"
VERSION = "0.2.0"
AUTHOR = "Adrian Povestca"

# --------------------------------------------------
# Directory Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
LOGS_DIR = BASE_DIR / "logs"

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

# --------------------------------------------------
# Retriever Configuration
# --------------------------------------------------
TOP_K_RESULTS = 3
MIN_SCORE_THRESHOLD = 0.1
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
    "to", "was", "will", "with", "i", "you", "he", "she", "it", "we",
    "they", "what", "which", "who", "when", "where", "why", "how",
}

# --------------------------------------------------
# Logging Configuration
# --------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "app.log"

# --------------------------------------------------
# AI Configuration (Phase 2: LLM Integration)
# --------------------------------------------------
# Using Groq (free tier, no credit card required) instead of paid OpenAI.
# Groq's API is OpenAI-compatible, so the same 'openai' Python package works —
# we just point it at Groq's server (OPENAI_BASE_URL) instead of OpenAI's.
DEFAULT_MODEL = "llama-3.1-8b-instant"
TEMPERATURE = 0.2
MAX_TOKENS = 1000
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")

# Master switch: if False (or no OPENAI_API_KEY present), the bot falls back
# to the original template-based responses from Phase 1.
USE_AI_GENERATION = os.getenv("USE_AI_GENERATION", "true").lower() == "true"

# --------------------------------------------------
# Vector Search Configuration (Phase 3)
# --------------------------------------------------
# Semantic search via ChromaDB + Sentence Transformers, as an alternative
# to the TF-IDF retriever. Understands meaning, not just exact keywords.
USE_VECTOR_SEARCH = os.getenv("USE_VECTOR_SEARCH", "true").lower() == "true"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHROMA_PERSIST_DIR = BASE_DIR / "chroma_db"