"""
Document loader for loading markdown files from the knowledge base.

This module reads all markdown files from the knowledge_base directory
and converts them into Document objects for retrieval and searching.
"""

import logging
from pathlib import Path
from typing import List

from config import KNOWLEDGE_BASE_DIR
from models import Document

logger = logging.getLogger(__name__)


def load_documents() -> List[Document]:
    """
    Load all markdown documents from the knowledge base directory.

    Returns:
        List of Document objects loaded from markdown files

    Raises:
        FileNotFoundError: If knowledge_base directory doesn't exist
        UnicodeDecodeError: If file encoding is invalid
    """
    logger.info(f"Loading documents from {KNOWLEDGE_BASE_DIR}")

    if not KNOWLEDGE_BASE_DIR.exists():
        logger.warning(f"Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}")
        return []

    documents: List[Document] = []
    markdown_files = sorted(KNOWLEDGE_BASE_DIR.glob("*.md"))

    if not markdown_files:
        logger.warning("No markdown files found in knowledge base directory")
        return documents

    for file_path in markdown_files:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                document = Document(
                    title=file_path.stem,
                    filename=file_path.name,
                    content=content,
                )
                documents.append(document)
                logger.debug(
                    f"Loaded document: {document.filename} ({len(content)} chars)"
                )
        except UnicodeDecodeError as e:
            logger.error(f"Error reading file {file_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading {file_path}: {e}")

    logger.info(f"Successfully loaded {len(documents)} document(s)")
    return documents


if __name__ == "__main__":
    # Configure basic logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    docs = load_documents()
    print(f"\nLoaded {len(docs)} document(s).\n")
    for doc in docs:
        print(f"• {doc.filename}")
