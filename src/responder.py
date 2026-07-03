"""
Response formatter for the AI Customer Support Playbook.

This module formats and presents search results to the user.
"""

import logging
from typing import List, Dict

from document import Document

logger = logging.getLogger(__name__)


def generate_response(search_results: List[Dict[str, any]]) -> str:
    """
    Generate a formatted response from search results.

    Args:
        search_results: List of result dicts with 'document' and 'score' keys

    Returns:
        Formatted response string for the user
    """
    if not search_results:
        logger.info("No search results found")
        return (
            "Sorry, I couldn't find any relevant information in the "
            "knowledge base. Please try rewording your question or "
            "contact our support team at support@shoesstore.com."
        )

    best_result = search_results[0]
    best_document: Document = best_result["document"]
    score = best_result["score"]

    logger.info(
        f"Returning top result: {best_document.filename} (score: {score:.4f})"
    )

    response = (
        f"📄 **{best_document.title}**\n\n"
        f"{best_document.content}\n\n"
        f"*Relevance: {score*100:.0f}%*"
    )

    return response
