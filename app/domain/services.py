"""Catalog service acting as a facade for the API layer."""

from __future__ import annotations

from typing import Dict, List

from .book import Book
from .catalog import Catalog
from .commands.add_book import AddBookCommand
from .commands.import_catalog import ImportCatalogCommand
from .commands.remove_book import RemoveBookCommand
from .commands.update_book import UpdateBookCommand
from .undo_manager import UndoManager
from ..infrastructure.factories.format_factory import FormatFactory


class CatalogService:
    """High-level operations used by FastAPI routes."""

    def __init__(self, catalog: Catalog, undo_manager: UndoManager, format_factory: FormatFactory) -> None:
        self._catalog = catalog
        self._undo_manager = undo_manager
        self._format_factory = format_factory

    def list_books(self) -> List[Dict[str, str | int]]:
        """Return all books as serializable dictionaries."""

        return [book.to_dict() for book in self._catalog.list_books()]

    def get_book(self, isbn: str) -> Dict[str, str | int]:
        """Retrieve a book by ISBN."""

        return self._catalog.get_book(isbn).to_dict()

    def add_book(self, payload: Dict[str, str | int]) -> Dict[str, str | int]:
        """Add a book using the command interface."""

        self._undo_manager.record_state(self._catalog.create_memento())
        command = AddBookCommand(self._catalog, Book.from_dict(payload))
        command.execute()
        return self.get_book(payload["isbn"])  # type: ignore[index]

    def update_book(self, isbn: str, payload: Dict[str, str | int]) -> Dict[str, str | int]:
        """Update a book via the command interface."""

        self._undo_manager.record_state(self._catalog.create_memento())
        updated = Book.from_dict({**payload, "isbn": isbn})
        command = UpdateBookCommand(self._catalog, isbn, updated)
        command.execute()
        return self.get_book(isbn)

    def remove_book(self, isbn: str) -> None:
        """Remove a book via the command interface."""

        self._undo_manager.record_state(self._catalog.create_memento())
        command = RemoveBookCommand(self._catalog, isbn)
        command.execute()

    def import_catalog(self, content: str, fmt: str) -> int:
        """Import books using the strategy selected by the factory."""

        strategy = self._format_factory.create(fmt)
        data = strategy.deserialize(content)
        books = {entry["isbn"]: Book.from_dict(entry) for entry in data}
        self._undo_manager.record_state(self._catalog.create_memento())
        command = ImportCatalogCommand(self._catalog, books)
        command.execute()
        return len(books)

    def export_catalog(self, fmt: str) -> str:
        """Export the current catalog using the chosen strategy."""

        strategy = self._format_factory.create(fmt)
        return strategy.serialize(self.list_books())

    def undo(self) -> Dict[str, object]:
        """Undo the latest operation and return metadata for the response."""

        self._undo_manager.undo(self._catalog)
        return {
            "books": self.list_books(),
            "remaining_undos": self._undo_manager.remaining(),
        }
