"""
document_loader.py
-------------------
Loads markdown files from the knowledge_base/ folder and parses them into
Document objects (see models.py). Replaces the previous loader.py duplicate.
"""

import re
from pathlib import Path
from typing import List

from models import Document
from logger import get_logger

logger = get_logger(__name__)

# Matches "# Category Title"
CATEGORY_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)
# Matches "## Question?" followed by everything up to the next "## " or end of file
QA_PATTERN = re.compile(r"^##\s+(.+?)\n(.*?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL)


class DocumentLoader:
    """Loads and parses all markdown files in a knowledge base directory."""

    def __init__(self, knowledge_base_dir: str):
        self.knowledge_base_dir = Path(knowledge_base_dir)

    def load_all(self) -> List[Document]:
        """Load every .md file in the knowledge base directory."""
        if not self.knowledge_base_dir.exists():
            logger.error(f"Knowledge base directory not found: {self.knowledge_base_dir}")
            return []

        documents: List[Document] = []
        md_files = sorted(self.knowledge_base_dir.glob("*.md"))

        for md_file in md_files:
            try:
                documents.extend(self._load_file(md_file))
            except Exception as exc:
                logger.warning(f"Failed to parse {md_file.name}: {exc}")

        logger.info(f"Loaded {len(documents)} Q&A entries from {len(md_files)} file(s)")
        return documents

    def _load_file(self, path: Path) -> List[Document]:
        text = path.read_text(encoding="utf-8")

        category_match = CATEGORY_PATTERN.search(text)
        category = category_match.group(1).strip() if category_match else path.stem.title()

        entries: List[Document] = []
        for match in QA_PATTERN.finditer(text):
            question = match.group(1).strip()
            answer = match.group(2).strip()
            if question and answer:
                entries.append(
                    Document(
                        category=category,
                        question=question,
                        answer=answer,
                        source_file=path.name,
                    )
                )
        return entries
