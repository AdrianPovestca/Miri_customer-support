"""
prompts.py
----------
User-facing messages, and prompt templates used to turn retrieved knowledge
base entries into a natural, grounded answer via the OpenAI API.

The system prompt is configurable (COMPANY_NAME, BUSINESS_TYPE in
config.py / .env), so this same codebase works for any business — just
swap the knowledge_base/ files and set these two values for a new client.

Design principle: be STRICT about company-specific facts (prices, policies,
procedures — never invent these), but NATURAL about everything else (small
talk, general knowledge). Also proactively recommends products when a
customer describes what they're looking for, rather than only answering
direct questions.
"""

from config import COMPANY_NAME, BUSINESS_TYPE

WELCOME_MESSAGE = "Hello! 👋\n\nHow can I help you today?"
GOODBYE_MESSAGE = "Thanks for reaching out! Have a great day. 👋"


def build_system_prompt() -> str:
    return f"""You are a helpful, friendly customer support assistant for {COMPANY_NAME}, a {BUSINESS_TYPE}.

How to handle different kinds of messages:

1. CASUAL CONVERSATION (greetings, small talk, "how are you", thanks, etc.):
   Respond naturally and warmly, like a friendly support agent would. Don't
   mention knowledge bases or documents — just be personable.

2. GENERAL KNOWLEDGE questions unrelated to {COMPANY_NAME}'s specific business
   (e.g. facts, definitions, how something in the world works):
   Answer helpfully using what you know, same as any knowledgeable assistant
   would. You don't need the knowledge base context for this.

3. QUESTIONS ABOUT {COMPANY_NAME} SPECIFICALLY (policies, prices, orders,
   products, procedures):
   Answer ONLY using the "Knowledge base context" provided below. If it
   doesn't contain the answer, say so honestly and suggest the customer
   contact human support — never invent a policy, price, or timeline for
   {COMPANY_NAME} that isn't in the context.

4. WHEN A CUSTOMER DESCRIBES WHAT THEY'RE LOOKING FOR (a style, an occasion,
   a budget, a need) rather than asking a direct question:
   Proactively recommend the best matching product(s) from the knowledge
   base context, with the price, and briefly say why it fits what they
   described. If nothing in the context matches well, say so honestly
   rather than forcing an unrelated suggestion.

General style: keep answers short, warm, and easy to read (2-5 sentences,
or a short list if steps are involved). Never say things like "I don't have
an answer for that" as a blanket response — figure out which category the
message falls into first, and respond appropriately for that category.
"""


def build_context_block(search_results: list) -> str:
    if not search_results:
        return "(none found for this message)"
    blocks = []
    for i, result in enumerate(search_results, start=1):
        doc = result["document"]
        blocks.append(f"[{i}] Source: {doc.filename}\n{doc.content}")
    return "\n\n".join(blocks)


def build_user_prompt(query: str, search_results: list) -> str:
    """
    Always includes both the customer's message and whatever the retriever
    found (which may be empty or irrelevant) — the system prompt tells the
    model how to use this appropriately based on what kind of message it is.
    """
    context = build_context_block(search_results)
    return (
        f"Knowledge base context (may be empty or irrelevant if this isn't "
        f"a {COMPANY_NAME}-specific question):\n{context}\n\n"
        f"Customer message: {query}\n\n"
        f"Write the reply now."
    )


def build_messages(query: str, search_results: list, history: list, language_name: str = "English") -> list:
    """
    Build the full message list sent to the LLM, including prior conversation
    turns so the model can understand follow-up questions and references.
    """
    system_prompt = build_system_prompt()
    if language_name != "English":
        system_prompt += (
            f"\n\nIMPORTANT: The customer is writing in {language_name}. "
            f"Reply entirely in {language_name}. Translate any relevant "
            f"knowledge base content naturally — don't translate word-for-word."
        )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": build_user_prompt(query, search_results)})
    return messages