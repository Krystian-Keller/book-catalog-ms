"""In-memory catalog that stores books keyed by ISBN."""

from __future__ import annotations

from typing import Dict, Iterable, List

from .book import Book
from .memento import CatalogMemento


class Catalog:
    """Simple collection acting as the aggregate root of the domain."""

    def __init__(self) -> None:
        self._books: Dict[str, Book] = {}

    def list_books(self) -> List[Book]:
        """Return the books as a list preserving insertion order."""

        return list(self._books.values())

    def get_book(self, isbn: str) -> Book:
        """Return the book or raise :class:`KeyError` when not present."""

        try:
            return self._books[isbn]
        except KeyError as exc:  # pragma: no cover - defensive
            raise KeyError(f"Book with ISBN {isbn} not found") from exc

    def add_book(self, book: Book) -> None:
        """Insert a new book enforcing ISBN uniqueness."""

        if book.isbn in self._books:
            raise ValueError(f"Book with ISBN {book.isbn} already exists")
        self._books[book.isbn] = book

    def update_book(self, isbn: str, book: Book) -> None:
        """Replace the stored book with the provided data."""

        if isbn not in self._books:
            raise KeyError(f"Book with ISBN {isbn} not found")
        self._books[isbn] = book

    def remove_book(self, isbn: str) -> Book:
        """Remove and return the book with the given ISBN."""

        if isbn not in self._books:
            raise KeyError(f"Book with ISBN {isbn} not found")
        return self._books.pop(isbn)

    def replace_all(self, books: Iterable[Book]) -> None:
        """Replace the catalog with the provided iterable of books."""

        self._books = {book.isbn: book for book in books}

    def create_memento(self) -> CatalogMemento:
        """Create a deep copy snapshot for the undo history."""

        snapshot = {isbn: Book.from_dict(book.to_dict()) for isbn, book in self._books.items()}
        return CatalogMemento(snapshot)

    def restore(self, memento: CatalogMemento) -> None:
        """Restore the catalog to the state stored in the memento."""

        self._books = {isbn: Book.from_dict(book.to_dict()) for isbn, book in memento.state.items()}
