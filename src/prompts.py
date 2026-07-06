"""
prompts.py
----------
User-facing messages, and prompt templates used to turn retrieved knowledge
base entries into a natural, grounded answer via the OpenAI API.
"""

# --------------------------------------------------
# User-facing messages (used by chatbot.py)
# --------------------------------------------------
WELCOME_MESSAGE = "Hello! 👋\n\nHow can I help you today?"

GOODBYE_MESSAGE = "Thanks for reaching out! Have a great day. 👋"

# --------------------------------------------------
# AI generation prompts (Phase 2: LLM Integration)
# --------------------------------------------------
SYSTEM_PROMPT = """You are a helpful, friendly customer support assistant for an online shoe store.

Rules you must always follow:
- Answer ONLY using the information provided in the "Knowledge base context" below.
- If the context does not contain enough information to answer, say so honestly and
  suggest the customer contact human support — do NOT make up policies, prices, or timelines.
- Keep answers short, warm, and easy to read (2-5 sentences, or a short list if steps are involved).
- Do not mention "the context" or "the documents" to the customer; just answer naturally,
  as a support agent who already knows this information.
"""


def build_context_block(search_results: list) -> str:
    """
    Turn retriever results (list of {"document": Document, "score": float})
    into a numbered context block for the prompt.
    """
    if not search_results:
        return "(no relevant knowledge base entries were found)"

    blocks = []
    for i, result in enumerate(search_results, start=1):
        doc = result["document"]
        blocks.append(f"[{i}] Source: {doc.filename}\n{doc.content}")
    return "\n\n".join(blocks)


def build_user_prompt(query: str, search_results: list) -> str:
    """Build the final user-turn prompt sent to the model."""
    context = build_context_block(search_results)
    return (
        f"Knowledge base context:\n{context}\n\n"
        f"Customer question: {query}\n\n"
        f"Write the reply to the customer now."
    )


def build_no_match_prompt(query: str) -> str:
    """Used when retrieval found nothing above the score threshold."""
    return (
        "No relevant knowledge base entries were found for this question.\n\n"
        f"Customer question: {query}\n\n"
        "Politely tell the customer you don't have that information on hand and "
        "suggest they reach out to human support for a definitive answer."
    )


def build_messages(query: str, search_results: list, history: list) -> list:
    """
    Build the full message list sent to the LLM, including prior conversation
    turns so the model can understand follow-up questions and references.

    Args:
        query: The current user question.
        search_results: Retriever results for the CURRENT question only.
        history: List of {"role": "user"/"assistant", "content": str} dicts
                 from earlier turns in this conversation (oldest first).

    Returns:
        A list of message dicts ready to pass to the chat completion API.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Include prior turns as-is, so the model has conversational context.
    messages.extend(history)

    # The current turn always includes the freshly retrieved knowledge base context.
    if search_results:
        current_prompt = build_user_prompt(query, search_results)
    else:
        current_prompt = build_no_match_prompt(query)

    messages.append({"role": "user", "content": current_prompt})
    return messages