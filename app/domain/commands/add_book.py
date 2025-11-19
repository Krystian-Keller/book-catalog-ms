"""Command responsible for adding a new book."""

from __future__ import annotations

from ..book import Book
from ..catalog import Catalog
from .base import Command


class AddBookCommand(Command):
    """Insert a book and support undo by removing it again."""

    def __init__(self, catalog: Catalog, book: Book) -> None:
        self._catalog = catalog
        self._book = book
        self._executed = False

    def execute(self) -> None:
        self._catalog.add_book(self._book)
        self._executed = True

    def undo(self) -> None:
        if not self._executed:
            return
        self._catalog.remove_book(self._book.isbn)
        self._executed = False
