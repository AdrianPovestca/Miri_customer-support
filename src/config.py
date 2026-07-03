"""
Configuration settings for the AI Customer Support Playbook.

This module stores global configuration values used throughout the project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# Project Information
# --------------------------------------------------

PROJECT_NAME = "AI Customer Support Playbook"
VERSION = "0.2.0"
AUTHOR = "Adrian Povestca"

# --------------------------------------------------
# Project Paths
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
# AI Configuration (Future)
# --------------------------------------------------

DEFAULT_MODEL = "gpt-4"
TEMPERATURE = 0.2
MAX_TOKENS = 1000
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
