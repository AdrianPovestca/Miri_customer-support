"""
Main chatbot application for the AI Customer Support Playbook.

This is the entry point for running the interactive customer support chatbot.
"""

import logging
import sys

from document_loader import load_documents
from retriever import search
from responder import generate_response
from prompts import WELCOME_MESSAGE, GOODBYE_MESSAGE
from logger import app_logger
from config import USE_VECTOR_SEARCH
from feedback import feedback_store

logger = logging.getLogger(__name__)

# Try to enable Phase 3 semantic search; fall back to TF-IDF (Phase 1) if
# chromadb/sentence-transformers aren't installed or anything else fails.
_semantic_search = None
if USE_VECTOR_SEARCH:
    try:
        from embeddings import semantic_search as _semantic_search
    except Exception as exc:
        logger.warning(f"Vector search unavailable, falling back to TF-IDF: {exc}")


def run_search(query: str):
    """Use semantic search if available, otherwise fall back to TF-IDF."""
    if _semantic_search is not None:
        try:
            return _semantic_search(query)
        except Exception as exc:
            logger.error(f"Semantic search failed, falling back to TF-IDF: {exc}")
    return search(query)


def build_search_query(query: str, history: list) -> str:
    """
    Enrich the search query with the customer's previous question, so
    retrieval understands short follow-ups like "What if it doesn't arrive?"
    that only make sense in light of what was just discussed.

    Only the retrieval step uses this enriched text — the LLM still sees
    the original, unmodified customer question in the prompt.
    """
    if not history:
        return query

    previous_user_messages = [turn["content"] for turn in history if turn["role"] == "user"]
    if not previous_user_messages:
        return query

    return f"{previous_user_messages[-1]} {query}"

# How many prior conversation turns (user+assistant pairs) to keep sending
# to the LLM for context. None/0 = unlimited (keeps the whole conversation).
MAX_HISTORY_TURNS = None


def display_banner() -> None:
    """Display the application banner."""
    print("\n" + "=" * 60)
    print("🤖 AI Customer Support Playbook")
    print("=" * 60 + "\n")


def display_loaded_documents(document_count: int, documents_info: list) -> None:
    """
    Display information about loaded documents.

    Args:
        document_count: Number of documents loaded
        documents_info: List of document filenames
    """
    print(f"Knowledge base loaded: {document_count} document(s)\n")

    if documents_info:
        for doc_name in documents_info:
            print(f"  • {doc_name}")
        print()


def display_welcome_message() -> None:
    """Display welcome message to user."""
    print("-" * 60)
    print(WELCOME_MESSAGE)
    print("-" * 60 + "\n")


def trim_history(history: list) -> list:
    """Keep only the last MAX_HISTORY_TURNS turns (each turn = 2 messages)."""
    if not MAX_HISTORY_TURNS:
        return history
    max_messages = MAX_HISTORY_TURNS * 2
    return history[-max_messages:]


def run_chatbot() -> None:
    """
    Run the interactive chatbot loop.

    Handles user queries, performs searches, and returns formatted responses.
    Keeps track of conversation history so follow-up questions and references
    to earlier turns are understood by the AI-generated responses.
    """
    logger.info("Starting AI Customer Support Chatbot")
    display_banner()

    # Load documents
    documents = load_documents()
    document_names = [doc.filename for doc in documents]

    if not documents:
        logger.error("No documents loaded from knowledge base")
        print("❌ Error: No documents found in knowledge base.")
        print("Please ensure knowledge base files are in the 'knowledge_base/' directory.")
        sys.exit(1)

    display_loaded_documents(len(documents), document_names)
    display_welcome_message()

    # Conversation history: list of {"role": "user"/"assistant", "content": str}
    conversation_history = []

    # Main interaction loop
    try:
        while True:
            # Get user input
            user_input = input("You: ").strip()

            # Check for exit commands
            if user_input.lower() in ("exit", "quit", "bye", "goodbye"):
                print("\nAssistant:")
                print(GOODBYE_MESSAGE)
                logger.info("User ended conversation")
                break

            # Reset conversation history on demand
            if user_input.lower() in ("reset", "clear", "new conversation"):
                conversation_history = []
                print("\nAssistant:")
                print("Sure, I've cleared our conversation history. What can I help you with?\n")
                continue

            # Skip empty queries
            if not user_input:
                print("\nAssistant:")
                print("Please enter a question.\n")
                continue

            logger.info(f"Processing query: {user_input}")

            # Search for relevant documents (semantic search, with TF-IDF fallback).
            # The search query is enriched with the previous question for context,
            # but the LLM still sees the original user_input as the customer's question.
            trimmed_history = trim_history(conversation_history)
            search_query = build_search_query(user_input, trimmed_history)
            search_results = run_search(search_query)

            # Generate response, taking prior conversation turns into account
            response = generate_response(
                search_results,
                user_input,
                trimmed_history,
            )

            print("\nAssistant:")
            print(response)
            print()

            # Store this turn in history for future context
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})

            # Quick feedback loop: ask if the response was helpful
            response_id = feedback_store.register_response(user_input, response)
            feedback_input = input("Was this helpful? (y/n, Enter to skip): ").strip().lower()
            if feedback_input == "y":
                feedback_store.record_feedback(response_id, "positive")
            elif feedback_input == "n":
                comment = input("Sorry about that — what went wrong? (optional, Enter to skip): ").strip()
                feedback_store.record_feedback(response_id, "negative", comment or None)
            print()

    except KeyboardInterrupt:
        print("\n\nAssistant:")
        print(GOODBYE_MESSAGE)
        logger.info("Chatbot interrupted by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Unexpected error in chatbot: {e}", exc_info=True)
        print("\n❌ An unexpected error occurred. Please try again.")
        raise
    finally:
        summary = feedback_store.summary()
        if summary["total_feedback"] > 0:
            print("-" * 60)
            print(f"Session feedback: {summary['positive']} 👍  {summary['negative']} 👎  "
                  f"({summary['satisfaction_rate_pct']}% satisfaction)")
            print("-" * 60)


if __name__ == "__main__":
    try:
        run_chatbot()
    except Exception as e:
        logger.critical(f"Chatbot crashed: {e}", exc_info=True)
        sys.exit(1)