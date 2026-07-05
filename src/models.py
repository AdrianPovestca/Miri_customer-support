"""
Data model for customer support documents.
This module defines the Document class used throughout the application.
"""

from dataclasses import dataclass


@dataclass
class Document:
    """
    Represents a customer support document or Q&A pair.

    Attributes:
        title: Document title or question heading
        filename: Source filename (e.g., 'account.md')
        content: Full document or answer text
    """
    title: str
    filename: str
    content: str

    def __repr__(self) -> str:
        """Return string representation of document."""
        return f"Document(title={self.title!r}, filename={self.filename!r})"
