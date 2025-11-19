"""Command replacing the entire catalog from imported data."""

from __future__ import annotations

from typing import Dict

from ..book import Book
from ..catalog import Catalog
from .base import Command


class ImportCatalogCommand(Command):
    """Swap the entire catalog content and keep a backup for undo."""

    def __init__(self, catalog: Catalog, imported_books: Dict[str, Book]) -> None:
        self._catalog = catalog
        self._imported_books = imported_books
        self._previous: Dict[str, Book] | None = None

    def execute(self) -> None:
        self._previous = {
            book.isbn: Book.from_dict(book.to_dict())
            for book in self._catalog.list_books()
        }
        self._catalog.replace_all(self._imported_books.values())

    def undo(self) -> None:
        if self._previous is None:
            return
        self._catalog.replace_all(self._previous.values())
        self._previous = None
