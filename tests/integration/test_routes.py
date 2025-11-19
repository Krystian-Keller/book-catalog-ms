"""Integration tests covering the FastAPI routes end-to-end."""

import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

BOOK = {
    "title": "Integration",
    "author": "Tester",
    "isbn": "999",
    "publisher": "Academic",
    "pages": 200,
}


def test_book_lifecycle() -> None:
    response = client.post("/catalog/books", json=BOOK)
    assert response.status_code == 201

    get_response = client.get(f"/catalog/books/{BOOK['isbn']}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Integration"

    update_payload = {
        "title": "Updated",
        "author": "Tester",
        "publisher": "Academic",
        "pages": 220,
    }
    update_response = client.put(f"/catalog/books/{BOOK['isbn']}", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated"

    delete_response = client.delete(f"/catalog/books/{BOOK['isbn']}")
    assert delete_response.status_code == 204


def test_import_export_and_undo() -> None:
    payload = {
        "catalog": [
            {
                "title": "Imported",
                "author": "Curator",
                "isbn": "101",
                "publisher": "Press",
                "pages": 300,
            }
        ]
    }

    import_response = client.post("/catalog/import", json={"format": "json", "content": json.dumps(payload)})
    assert import_response.status_code == 200
    assert import_response.json()["count"] == 1

    export_response = client.post("/catalog/export", json={"format": "json"})
    assert export_response.status_code == 200
    exported = json.loads(export_response.json()["content"])
    assert exported["catalog"][0]["title"] == "Imported"

    undo_response = client.post("/catalog/undo")
    assert undo_response.status_code == 200
    body = undo_response.json()
    assert body["books"] == []
    assert body["remaining_undos"] >= 0
