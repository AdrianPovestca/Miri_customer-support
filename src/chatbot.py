"""
AI Customer Support Playbook

Main application entry point.
"""

from loader import load_documents

def show_banner():
    print("=" * 50)
    print("🤖 AI Customer Support Playbook")
    print("=" * 50)


    files = list(KNOWLEDGE_BASE_PATH.glob("*.md"))

    print(f"\nKnowledge base loaded: {len(files)} document(s)\n")

    for file in files:
        print(f"• {file.name}")


def main():
    show_banner()

documents = load_documents()

print(f"\nKnowledge base loaded: {len(documents)} document(s)\n")

for document in documents:
    print(f"• {document['filename']}")


if __name__ == "__main__":
    main()
