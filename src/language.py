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
    from langdetect import detect_langs, DetectorFactory, LangDetectException
    DetectorFactory.seed = 0  # makes detection deterministic, not random per run
    _detector_available = True
except ImportError:
    logger.warning("langdetect not installed; multi-language detection disabled, defaulting to English.")

# langdetect is unreliable on short or ambiguous text (e.g. "Do you accept
# PayPal?" can get misdetected as Spanish). To avoid confidently answering
# in the wrong language, we only trust a non-English detection when the
# text is long enough AND the model's confidence is high.
MIN_LENGTH_FOR_DETECTION = 12
MIN_CONFIDENCE = 0.90


def detect_language(text: str) -> str:
    """
    Detect the ISO 639-1 language code of the given text.
    Defaults to "en" whenever detection is unavailable, the text is too
    short, or the model isn't confident enough — short/ambiguous English
    text is far more common in this context than genuinely short
    non-English questions, so English is the safer default.
    """
    if not _detector_available or not text or len(text.strip()) < MIN_LENGTH_FOR_DETECTION:
        return "en"

    try:
        candidates = detect_langs(text)
        if not candidates:
            return "en"
        best = candidates[0]
        if best.lang == "en" or best.prob < MIN_CONFIDENCE:
            return "en"
        return best.lang
    except LangDetectException:
        return "en"


def language_name(code: str) -> str:
    """Human-readable language name for a given code, for use in prompts."""
    return LANGUAGE_NAMES.get(code, code)