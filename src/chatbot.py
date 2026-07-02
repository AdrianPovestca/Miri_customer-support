"""
AI Customer Support Playbook

Main application entry point.
"""

from loader import load_documents
from retriever import search
from responder import generate_response
from prompts import WELCOME_MESSAGE


def show_banner():
    """Display the application banner."""
    print("=" * 50)
    print("🤖 AI Customer Support Playbook")
    print("=" * 50)


def main():
    """Run the chatbot."""

    show_banner()

    documents = load_documents()

    print(f"\nKnowledge base loaded: {len(documents)} document(s)\n")

    for document in documents:
        print(f"• {document.filename}")

    print("\n" + "-" * 50)
    print(WELCOME_MESSAGE)

    while True:

        query = input("You: ").strip()

        if query.lower() == "exit":
            print("\nAssistant:")
            print("Goodbye! 👋")
            break

        if not query:
            print("\nAssistant:")
            print("Please enter a question.\n")
            continue

        results = search(query)

        response = generate_response(results)

        print("\nAssistant:\n")
        print(response)
        print()


if __name__ == "__main__":
    main()
