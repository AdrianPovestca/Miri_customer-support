"""
Response generator for the AI Customer Support Playbook.
"""

from models import Document


def generate_response(results):
    """
    Generate a response from the highest-ranked document.

    Args:
        results (list): Search results returned by the retriever.

    Returns:
        str: Response shown to the user.
    """

    if not results:
        return (
            "Sorry, I couldn't find any relevant information in the "
            "knowledge base."
        )

    best_document: Document = results[0]["document"]

    response = (
        f"📄 {best_document.title}\n\n"
        f"{best_document.content}"
    )

    return response
