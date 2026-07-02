"""
Document Loader

Loads all Markdown files from the knowledge base.
"""

from config import KNOWLEDGE_BASE_DIR
from models import Document


def load_documents():
    """
    Load all Markdown documents from the knowledge base.

    Returns:
        list[Document]: List of loaded documents.
    """

    documents = []

    markdown_files = sorted(KNOWLEDGE_BASE_DIR.glob("*.md"))

    for file_path in markdown_files:
        with open(file_path, "r", encoding="utf-8") as file:

            documents.append(
                Document(
                    title=file_path.stem,
                    filename=file_path.name,
                    content=file.read(),
                )
            )

    return documents


if __name__ == "__main__":

    docs = load_documents()

    print(f"Loaded {len(docs)} document(s).\n")

    for doc in docs:
        print(f"• {doc.filename}")
