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
    history = history or []

    if _client is not None and query:
        try:
            return _generate_ai_response(query, search_results, history)
        except Exception as exc:
            logger.error(f"OpenAI/Groq generation failed, falling back to template: {exc}")

    return _template_response(search_results)


# ------------------------------------------------------------------
# AI-powered generation (Phase 2)
# ------------------------------------------------------------------
def _generate_ai_response(query: str, search_results: List[Dict], history: List[Dict]) -> str:
    messages = build_messages(query, search_results, history)

    completion = _client.chat.completions.create(
        model=DEFAULT_MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        messages=messages,
    )
    answer = completion.choices[0].message.content.strip()
    logger.info(f"AI-generated response for query: {query[:60]!r} (history turns: {len(history)})")
    return answer


# ------------------------------------------------------------------
# Original template-based fallback (Phase 1 behavior, preserved)
# ------------------------------------------------------------------
def _template_response(search_results: List[Dict]) -> str:
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

    return "\n".join(lines)