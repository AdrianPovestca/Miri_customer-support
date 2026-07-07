"""
language.py
-----------
Phase 5: Advanced Features — multi-language support.

Detects the language of the customer's question, so the LLM can be
instructed to reply in that same language, even though the knowledge base
itself is written in English.
"""

import logging

logger = logging.getLogger(__name__)

# Human-readable names for the language codes we're most likely to see,
# given the customer support context. langdetect returns ISO 639-1 codes.
LANGUAGE_NAMES = {
    "en": "English",
    "ro": "Romanian",
    "de": "German",
    "ru": "Russian",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "pl": "Polish",
    "uk": "Ukrainian",
    "tr": "Turkish",
}

_detector_available = False
try:
    from langdetect import detect, DetectorFactory, LangDetectException
    DetectorFactory.seed = 0  # makes detection deterministic, not random per run
    _detector_available = True
except ImportError:
    logger.warning("langdetect not installed; multi-language detection disabled, defaulting to English.")


def detect_language(text: str) -> str:
    """
    Detect the ISO 639-1 language code of the given text.
    Falls back to "en" if detection isn't available or fails
    (e.g. the text is too short to reliably detect, like "hi" or "ok").
    """
    if not _detector_available or not text or len(text.strip()) < 3:
        return "en"

    try:
        return detect(text)
    except LangDetectException:
        return "en"


def language_name(code: str) -> str:
    """Human-readable language name for a given code, for use in prompts."""
    return LANGUAGE_NAMES.get(code, code)