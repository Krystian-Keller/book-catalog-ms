"""Catalog and book domain unit tests."""

import pytest

from app.domain.book import Book
from app.domain.catalog import Catalog


def make_book(isbn: str = "001") -> Book:
    return Book(title="Title", author="Author", isbn=isbn, publisher="Press", pages=123)


def test_create_book_with_valid_data() -> None:
    catalog = Catalog()

    catalog.add_book(make_book())

    stored = catalog.get_book("001")
    assert stored.title == "Title"
    assert stored.pages == 123


def test_update_existing_book() -> None:
    catalog = Catalog()
    catalog.add_book(make_book())

    catalog.update_book("001", Book(title="Updated", author="Author", isbn="001", publisher="Press", pages=150))

    updated = catalog.get_book("001")
    assert updated.title == "Updated"
    assert updated.pages == 150


def test_remove_book_by_isbn() -> None:
    catalog = Catalog()
    catalog.add_book(make_book())

    removed = catalog.remove_book("001")

    assert removed.isbn == "001"
    assert catalog.list_books() == []


def test_reject_duplicate_isbn() -> None:
    catalog = Catalog()
    catalog.add_book(make_book())

    with pytest.raises(ValueError):
        catalog.add_book(make_book())


def test_missing_isbn_raises_error() -> None:
    catalog = Catalog()

    with pytest.raises(KeyError):
        catalog.get_book("missing")
