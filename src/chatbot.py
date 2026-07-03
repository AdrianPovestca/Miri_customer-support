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

logger = logging.getLogger(__name__)


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


def run_chatbot() -> None:
    """
    Run the interactive chatbot loop.

    Handles user queries, performs searches, and returns formatted responses.
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

            # Skip empty queries
            if not user_input:
                print("\nAssistant:")
                print("Please enter a question.\n")
                continue

            logger.info(f"Processing query: {user_input}")

            # Search for relevant documents
            search_results = search(user_input)

            # Generate and display response
            response = generate_response(search_results)

            print("\nAssistant:")
            print(response)
            print()

    except KeyboardInterrupt:
        print("\n\nAssistant:")
        print(GOODBYE_MESSAGE)
        logger.info("Chatbot interrupted by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Unexpected error in chatbot: {e}", exc_info=True)
        print("\n❌ An unexpected error occurred. Please try again.")
        raise


if __name__ == "__main__":
    try:
        run_chatbot()
    except Exception as e:
        logger.critical(f"Chatbot crashed: {e}", exc_info=True)
        sys.exit(1)
