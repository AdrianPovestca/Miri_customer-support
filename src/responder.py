"""
Response generator for the AI Customer Support Playbook.
"""


def generate_response(results):
    """
    Generate a response from the retrieved documents.
    """

    if not results:
        return (
            "Sorry, I couldn't find any relevant information in the "
            "knowledge base."
        )

    best_document = results[0]["document"]

    return best_document["content"]
