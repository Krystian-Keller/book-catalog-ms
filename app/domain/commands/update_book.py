"""Command replacing the information of an existing book."""

from __future__ import annotations

from typing import Optional

from ..book import Book
from ..catalog import Catalog
from .base import Command


class UpdateBookCommand(Command):
    """Update a book and track the previous copy for undo."""

    def __init__(self, catalog: Catalog, isbn: str, replacement: Book) -> None:
        self._catalog = catalog
        self._isbn = isbn
        self._replacement = replacement
        self._previous: Optional[Book] = None

    def execute(self) -> None:
        self._previous = self._catalog.get_book(self._isbn)
        self._catalog.update_book(self._isbn, self._replacement)

    def undo(self) -> None:
        if self._previous is None:
            return
        self._catalog.update_book(self._isbn, self._previous)
        self._previous = None
