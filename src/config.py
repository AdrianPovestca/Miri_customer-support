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
VERSION = "0.1.0"
AUTHOR = "Adrian Povestca"

# --------------------------------------------------
# Project Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DOCS_DIR = BASE_DIR / "docs"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"

# --------------------------------------------------
# AI Configuration
# --------------------------------------------------

DEFAULT_MODEL = "gpt-4.1"

TOP_K_RESULTS = 3

TEMPERATURE = 0.2

MAX_TOKENS = 1000

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
