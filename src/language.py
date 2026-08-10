"""
language.py
-----------
Phase 5: Advanced Features — multi-language support.

Detects the language of the customer's question, so the LLM can be
instructed to reply in that same language, even though the knowledge base
itself may be written in a different language.
"""

import logging

logger = logging.getLogger(__name__)

# Human-readable names for language codes langdetect can return (ISO 639-1).
# This list is intentionally broad so almost any detected language gets a
# proper name in the prompt instead of falling back to a raw code.
LANGUAGE_NAMES = {
    "en": "English", "ro": "Romanian", "de": "German", "ru": "Russian",
    "fr": "French", "es": "Spanish", "it": "Italian", "pt": "Portuguese",
    "nl": "Dutch", "pl": "Polish", "uk": "Ukrainian", "tr": "Turkish",
    "el": "Greek", "cs": "Czech", "sk": "Slovak", "hu": "Hungarian",
    "sv": "Swedish", "no": "Norwegian", "da": "Danish", "fi": "Finnish",
    "bg": "Bulgarian", "hr": "Croatian", "sr": "Serbian", "sl": "Slovenian",
    "lt": "Lithuanian", "lv": "Latvian", "et": "Estonian",
    "ar": "Arabic", "he": "Hebrew", "fa": "Persian", "ur": "Urdu",
    "hi": "Hindi", "bn": "Bengali", "ta": "Tamil", "te": "Telugu",
    "zh-cn": "Chinese", "zh-tw": "Chinese (Traditional)", "ja": "Japanese",
    "ko": "Korean", "vi": "Vietnamese", "th": "Thai", "id": "Indonesian",
    "ms": "Malay", "tl": "Filipino", "sw": "Swahili", "af": "Afrikaans",
    "ca": "Catalan", "eu": "Basque", "gl": "Galician", "is": "Icelandic",
    "mk": "Macedonian", "sq": "Albanian", "hy": "Armenian", "ka": "Georgian",
    "az": "Azerbaijani", "kk": "Kazakh", "uz": "Uzbek", "mn": "Mongolian",
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