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
    """Main application."""

    show_banner()

    documents = load_documents()

    print(f"\nKnowledge base loaded: {len(documents)} document(s)\n")

    for document in documents:
        print(f"• {document['filename']}")

    print("\n" + "-" * 40)
    print(WELCOME_MESSAGE)

    while True:

        query = input("You: ")

        if query.lower() == "exit":
            print("\nGoodbye! 👋")
            break

        results = search(query)

        if not results:
            print("\nAssistant:")
            print("Sorry, I couldn't find any relevant information.\n")
            continue

        print("\nAssistant found these relevant document(s):")

        for item in results:
            print(f"- {item['document']['filename']} (score: {item['score']})")

        print()

if __name__ == "__main__":
    main()
