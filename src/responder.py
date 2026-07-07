"""
responder.py
------------
Turns retriever results into the final reply shown to the customer.

Phase 2 addition: if an OPENAI_API_KEY is configured and USE_AI_GENERATION
is on, this asks the LLM (via Groq's free, OpenAI-compatible API) to write
a natural answer grounded in the retrieved knowledge base entries, taking
the ongoing conversation history into account. If it's disabled,
unconfigured, or the API call fails for any reason, it transparently
falls back to the original Phase 1 template-based formatting.
"""

import logging
from typing import List, Dict, Optional

from config import OPENAI_API_KEY, OPENAI_BASE_URL, USE_AI_GENERATION, DEFAULT_MODEL, TEMPERATURE, MAX_TOKENS
from prompts import build_messages
from language import detect_language, language_name as get_language_name

logger = logging.getLogger(__name__)

_client = None
if USE_AI_GENERATION and OPENAI_API_KEY:
    try:
        from openai import OpenAI
        _client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    except ImportError:
        logger.warning(
            "USE_AI_GENERATION is on but the 'openai' package isn't installed. "
            "Run: pip install openai. Falling back to template responses."
        )


def generate_response(
    search_results: List[Dict],
    query: Optional[str] = None,
    history: Optional[List[Dict]] = None,
) -> str:
    """
    Generate the final response text shown to the user.

    Args:
        search_results: List of {"document": Document, "score": float} from retriever.search()
        query: The original user question. Needed for AI generation; if omitted,
               the function falls back to the template-based response.
        history: List of {"role": "user"/"assistant", "content": str} dicts from
                 earlier turns in this conversation (oldest first). Optional —
                 omitting it just means the bot won't recall earlier turns.

    Returns:
        The response string to display to the customer.
    """
    text, _used_ai = generate_response_with_meta(search_results, query, history)
    return text


def generate_response_with_meta(
    search_results: List[Dict],
    query: Optional[str] = None,
    history: Optional[List[Dict]] = None,
):
    """
    Same as generate_response(), but also reports whether AI generation was
    actually used for this call (vs. falling back to the template). Used by
    the API's analytics/monitoring (Phase 4) to track the real AI usage rate.

    Returns:
        (response_text: str, used_ai_generation: bool)
    """
    history = history or []

    detected_lang = detect_language(query) if query else "en"

    if _client is not None and query:
        try:
            return _generate_ai_response(query, search_results, history, detected_lang), True
        except Exception as exc:
            logger.error(f"OpenAI/Groq generation failed, falling back to template: {exc}")

    return _template_response(search_results, detected_lang), False


# ------------------------------------------------------------------
# AI-powered generation (Phase 2, multi-language in Phase 5)
# ------------------------------------------------------------------
def _generate_ai_response(query: str, search_results: List[Dict], history: List[Dict], detected_lang: str = "en") -> str:
    lang_name = get_language_name(detected_lang)
    messages = build_messages(query, search_results, history, lang_name)

    completion = _client.chat.completions.create(
        model=DEFAULT_MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        messages=messages,
    )
    answer = completion.choices[0].message.content.strip()
    logger.info(f"AI-generated response ({lang_name}) for query: {query[:60]!r} (history turns: {len(history)})")
    return answer


# ------------------------------------------------------------------
# Original template-based fallback (Phase 1 behavior, preserved)
# ------------------------------------------------------------------
def _template_response(search_results: List[Dict], detected_lang: str = "en") -> str:
    if not search_results:
        return (
            "I couldn't find anything specific about that in our help center. "
            "Could you rephrase your question, or would you like me to connect "
            "you with a human agent?"
        )

    best_doc = search_results[0]["document"]
    lines = [best_doc.content.strip()]

    if len(search_results) > 1:
        lines.append("\nYou might also find these helpful:")
        for result in search_results[1:]:
            lines.append(f"• {result['document'].title}")

    # Honest limitation: the template fallback can only return English text
    # (it's raw knowledge base content, not AI-translated). Let non-English
    # speakers know why the reply looks like this.
    if detected_lang != "en":
        lang_name = get_language_name(detected_lang)
        lines.append(
            f"\n(Note: full support for {lang_name} requires AI generation to be "
            f"enabled; this answer is shown in English for now.)"
        )

    return "\n".join(lines)