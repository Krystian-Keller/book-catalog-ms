"""Command removing a book from the catalog."""

from __future__ import annotations

from typing import Optional

from ..book import Book
from ..catalog import Catalog
from .base import Command


class RemoveBookCommand(Command):
    """Remove a book and allow undo by re-inserting it."""

    def __init__(self, catalog: Catalog, isbn: str) -> None:
        self._catalog = catalog
        self._isbn = isbn
        self._removed: Optional[Book] = None

    def execute(self) -> None:
        self._removed = self._catalog.remove_book(self._isbn)

    def undo(self) -> None:
        if self._removed is None:
            return
        self._catalog.add_book(self._removed)
        self._removed = None
