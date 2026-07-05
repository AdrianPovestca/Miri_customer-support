"""
responder.py
------------
Turns retrieved Document objects into a final reply to the customer.

Phase 2 addition: if OpenAI generation is enabled and configured, the
Responder asks the LLM to synthesize a natural answer grounded in the
retrieved knowledge base entries. If it's disabled, unconfigured, or the
API call fails for any reason, it transparently falls back to the original
Phase 1 template-based formatting so the bot never breaks.
"""

from typing import List

from models import Document
from config import settings
from prompts import SYSTEM_PROMPT, build_user_prompt, build_no_match_prompt
from logger import get_logger

logger = get_logger(__name__)


class Responder:
    def __init__(self):
        self._client = None
        if settings.ai_generation_enabled:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=settings.openai_api_key)
            except ImportError:
                logger.warning(
                    "USE_AI_GENERATION is on but the 'openai' package isn't installed. "
                    "Run: pip install openai. Falling back to template responses."
                )

    def respond(self, query: str, documents: List[Document]) -> str:
        """Main entry point: returns the text to show the user."""
        if self._client is not None:
            try:
                return self._generate_ai_response(query, documents)
            except Exception as exc:
                logger.error(f"OpenAI generation failed, falling back to template: {exc}")

        return self._template_response(query, documents)

    # ------------------------------------------------------------------
    # AI-powered generation (Phase 2)
    # ------------------------------------------------------------------
    def _generate_ai_response(self, query: str, documents: List[Document]) -> str:
        if documents:
            user_prompt = build_user_prompt(query, documents)
        else:
            user_prompt = build_no_match_prompt(query)

        completion = self._client.chat.completions.create(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        answer = completion.choices[0].message.content.strip()
        logger.info(f"AI-generated response for query: {query[:60]!r}")
        return answer

    # ------------------------------------------------------------------
    # Original template-based fallback (Phase 1 behavior, preserved)
    # ------------------------------------------------------------------
    def _template_response(self, query: str, documents: List[Document]) -> str:
        if not documents:
            return (
                "I couldn't find anything specific about that in our help center. "
                "Could you rephrase your question, or would you like me to connect "
                "you with a human agent?"
            )

        best = documents[0]
        lines = [best.answer]

        if len(documents) > 1:
            lines.append("\nYou might also find these helpful:")
            for doc in documents[1:]:
                lines.append(f"• {doc.question}")

        return "\n".join(lines)
