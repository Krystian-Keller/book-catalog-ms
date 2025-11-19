"""Command pattern unit tests."""

from app.domain.book import Book
from app.domain.catalog import Catalog
from app.domain.commands.add_book import AddBookCommand
from app.domain.commands.import_catalog import ImportCatalogCommand
from app.domain.commands.remove_book import RemoveBookCommand
from app.domain.commands.update_book import UpdateBookCommand


def make_book(isbn: str = "001") -> Book:
    return Book(title="Sample", author="Author", isbn=isbn, publisher="Press", pages=100)


def test_add_book_command_execute_and_undo() -> None:
    catalog = Catalog()
    command = AddBookCommand(catalog, make_book())

    command.execute()
    assert catalog.get_book("001").title == "Sample"

    command.undo()
    assert catalog.list_books() == []


def test_remove_book_command_execute_and_undo() -> None:
    catalog = Catalog()
    catalog.add_book(make_book())
    command = RemoveBookCommand(catalog, "001")

    command.execute()
    assert catalog.list_books() == []

    command.undo()
    assert catalog.get_book("001").title == "Sample"


def test_update_book_command_execute_and_undo() -> None:
    catalog = Catalog()
    catalog.add_book(make_book())
    new_book = Book(title="Updated", author="Author", isbn="001", publisher="Press", pages=200)
    command = UpdateBookCommand(catalog, "001", new_book)

    command.execute()
    assert catalog.get_book("001").title == "Updated"

    command.undo()
    assert catalog.get_book("001").title == "Sample"


def test_import_catalog_command_execute_and_undo() -> None:
    catalog = Catalog()
    catalog.add_book(make_book("111"))
    imported_books = {isbn: make_book(isbn) for isbn in ["222", "333"]}
    command = ImportCatalogCommand(catalog, imported_books)

    command.execute()
    assert sorted(book.isbn for book in catalog.list_books()) == ["222", "333"]

    command.undo()
    assert sorted(book.isbn for book in catalog.list_books()) == ["111"]
