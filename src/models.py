"""
models.py
---------
Consolidated data models for the AI Customer Support Playbook.

This file replaces the previous document.py + models.py duplication.
Everything that represents "a piece of knowledge base content" lives here.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Document:
    """
    Represents a single Q&A entry extracted from a knowledge_base/*.md file.

    Attributes:
        category: The top-level heading of the file (e.g. "Account Management").
        question: The question text (from a "## " heading).
        answer: The answer text that follows the question heading.
        source_file: Filename the entry was loaded from (e.g. "account.md").
        score: Optional relevance score, set by the retriever at query time.
    """
    category: str
    question: str
    answer: str
    source_file: str
    score: float = field(default=0.0)

    @property
    def content(self) -> str:
        """Combined text used for search/indexing."""
        return f"{self.question}\n{self.answer}"

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "question": self.question,
            "answer": self.answer,
            "source_file": self.source_file,
            "score": self.score,
        }

    def __repr__(self) -> str:
        return f"Document(source={self.source_file!r}, question={self.question[:50]!r}...)"


@dataclass
class ConversationTurn:
    """One turn of context history, used for multi-turn context management."""
    role: str          # "user" or "assistant"
    content: str
    retrieved_sources: Optional[list] = None
