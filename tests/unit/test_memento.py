"""Tests covering the memento-based undo manager."""

import pytest

from app.domain.book import Book
from app.domain.catalog import Catalog
from app.domain.undo_manager import UndoManager


def make_catalog() -> Catalog:
    catalog = Catalog()
    catalog.add_book(Book(title="Base", author="Author", isbn="AAA", publisher="Press", pages=100))
    return catalog


def test_undo_restores_previous_state() -> None:
    catalog = make_catalog()
    undo = UndoManager(limit=5)
    undo.record_state(catalog.create_memento())
    catalog.add_book(Book(title="Second", author="B", isbn="BBB", publisher="Press", pages=120))

    undo.undo(catalog)

    assert [book.isbn for book in catalog.list_books()] == ["AAA"]


def test_history_limit_is_enforced() -> None:
    catalog = make_catalog()
    undo = UndoManager(limit=2)
    for idx in range(3):
        undo.record_state(catalog.create_memento())
        catalog.update_book(
            "AAA",
            Book(title=f"Title {idx}", author="Author", isbn="AAA", publisher="Press", pages=100 + idx),
        )

    undo.undo(catalog)
    assert catalog.get_book("AAA").title == "Title 1"

    undo.undo(catalog)
    assert catalog.get_book("AAA").title == "Title 0"

    with pytest.raises(ValueError):
        undo.undo(catalog)


def test_remaining_reports_available_states() -> None:
    catalog = make_catalog()
    undo = UndoManager(limit=3)

    undo.record_state(catalog.create_memento())
    catalog.update_book("AAA", Book(title="One", author="Author", isbn="AAA", publisher="Press", pages=101))
    assert undo.remaining() == 1

    undo.record_state(catalog.create_memento())
    catalog.update_book("AAA", Book(title="Two", author="Author", isbn="AAA", publisher="Press", pages=102))
    assert undo.remaining() == 2

    undo.undo(catalog)
    assert undo.remaining() == 1


def test_history_limit_default_cap() -> None:
    catalog = make_catalog()
    undo = UndoManager()

    for idx in range(12):
        undo.record_state(catalog.create_memento())
        catalog.update_book(
            "AAA",
            Book(title=f"Title {idx}", author="Author", isbn="AAA", publisher="Press", pages=100 + idx),
        )

    assert undo.remaining() == 10


def test_undo_without_history_raises_error() -> None:
    catalog = make_catalog()
    undo = UndoManager(limit=2)

    with pytest.raises(ValueError):
        undo.undo(catalog)

    undo.record_state(catalog.create_memento())
    undo.undo(catalog)
    assert undo.remaining() == 0
