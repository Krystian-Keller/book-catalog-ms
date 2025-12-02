"""Integration tests covering the FastAPI routes end-to-end."""

import json
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.api.routes import get_service
from app.domain.catalog import Catalog
from app.domain.services import CatalogService
from app.domain.undo_manager import UndoManager
from app.infrastructure.factories.format_factory import FormatFactory
from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    service = CatalogService(Catalog(), UndoManager(), FormatFactory())
    app.dependency_overrides[get_service] = lambda: service
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def sample_book(isbn: str = "999") -> dict[str, str | int]:
    return {
        "title": "Integration",
        "author": "Tester",
        "isbn": isbn,
        "publisher": "Academic",
        "pages": 200,
    }


def test_book_lifecycle(client: TestClient) -> None:
    create_response = client.post("/catalog/books", json=sample_book())
    assert create_response.status_code == 201

    list_response = client.get("/catalog/books")
    assert list_response.status_code == 200
    assert any(book["isbn"] == "999" for book in list_response.json())

    get_response = client.get("/catalog/books/999")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Integration"

    update_payload = {
        "title": "Updated",
        "author": "Tester",
        "publisher": "Academic",
        "pages": 220,
    }
    update_response = client.put("/catalog/books/999", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated"

    delete_response = client.delete("/catalog/books/999")
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"


def test_import_export_json(client: TestClient) -> None:
    payload = {"catalog": [sample_book("101")]}  # type: ignore[list-item]

    import_response = client.post(
        "/catalog/import", json={"format": "json", "content": json.dumps(payload)}
    )
    assert import_response.status_code == 200
    assert import_response.json()["count"] == 1

    export_response = client.post("/catalog/export", json={"format": "json"})
    assert export_response.status_code == 200
    exported = json.loads(export_response.json()["content"])
    assert exported["catalog"][0]["isbn"] == "101"


def test_import_export_xml(client: TestClient) -> None:
    xml_payload = (
        "<catalog><book><title>XML</title><author>Tester</author><isbn>202"  # noqa: E501
        "</isbn><publisher>Press</publisher><pages>150</pages></book></catalog>"
    )

    import_response = client.post("/catalog/import", json={"format": "xml", "content": xml_payload})
    assert import_response.status_code == 200
    assert import_response.json()["count"] == 1

    export_response = client.post("/catalog/export", json={"format": "xml"})
    assert export_response.status_code == 200
    assert "<isbn>202</isbn>" in export_response.json()["content"]


def test_invalid_format_returns_error(client: TestClient) -> None:
    import_response = client.post("/catalog/import", json={"format": "yaml", "content": ""})
    assert import_response.status_code in {400, 422}

    export_response = client.post("/catalog/export", json={"format": "yaml"})
    assert export_response.status_code in {400, 422}



def test_import_invalid_payload_returns_error(client: TestClient) -> None:
    response = client.post("/catalog/import", json={"format": "json", "content": "{invalid}"})
    assert response.status_code == 400



def test_undo_flow_and_multiple_undos(client: TestClient) -> None:
    client.post("/catalog/books", json=sample_book("444"))
    client.put(
        "/catalog/books/444",
        json={"title": "Changed", "author": "Tester", "publisher": "Press", "pages": 210},
    )
    client.delete("/catalog/books/444")

    first_undo = client.post("/catalog/undo")
    assert first_undo.status_code == 200
    assert first_undo.json()["books"][0]["title"] == "Changed"

    second_undo = client.post("/catalog/undo")
    assert second_undo.status_code == 200
    assert second_undo.json()["books"][0]["title"] == "Integration"

    third_undo = client.post("/catalog/undo")
    assert third_undo.status_code == 200
    assert third_undo.json()["books"] == []

    final_undo = client.post("/catalog/undo")
    assert final_undo.status_code == 400
