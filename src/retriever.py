"""
Simple keyword-based retriever.

This is the first version of our retrieval system.
Later it will be replaced with semantic search using embeddings.
"""

from config import TOP_K_RESULTS
from loader import load_documents


def search(query: str):
    """
    Search the knowledge base using simple keyword matching.

    Args:
        query (str): User question.

    Returns:
        list: Ranked search results.
    """

    query = query.lower()

    results = []

    documents = load_documents()

    for document in documents:

        score = 0

        words = query.split()

        content = document.content.lower()

        for word in words:

            if word in content:
                score += 1

        if score > 0:

            results.append(
                {
                    "document": document,
                    "score": score,
                }
            )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:TOP_K_RESULTS]
