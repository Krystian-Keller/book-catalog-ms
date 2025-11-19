"""Domain entity representing a single book."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Book:
    """Value object capturing the data attributes of a book."""

    title: str
    author: str
    isbn: str
    publisher: str
    pages: int

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation that is safe for serialization."""

        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "publisher": self.publisher,
            "pages": self.pages,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Book":
        """Build a :class:`Book` instance from a plain dictionary."""

        return cls(
            title=payload["title"],
            author=payload["author"],
            isbn=payload["isbn"],
            publisher=payload["publisher"],
            pages=int(payload["pages"]),
        )
