"""Extremely small HTTP client for the FastAPI stub."""

from __future__ import annotations

import json
from typing import Any, Dict

from . import status


class Response:
    """Mimics the subset of ``requests.Response`` accessed in tests."""

    def __init__(self, status_code: int, data: Any) -> None:
        self.status_code = status_code
        self._data = data

    def json(self) -> Any:
        return self._data

    @property
    def text(self) -> str:
        if isinstance(self._data, (dict, list)):
            return json.dumps(self._data)
        return str(self._data)


class TestClient:
    """Send fake HTTP requests directly to the stub FastAPI app."""

    def __init__(self, app: Any) -> None:
        self.app = app

    def _request(self, method: str, path: str, json: Dict[str, Any] | None = None) -> Response:
        status_code, payload = self.app.handle_request(method, path, json or {})
        return Response(status_code, payload)

    def get(self, path: str) -> Response:
        return self._request("GET", path)

    def post(self, path: str, json: Dict[str, Any] | None = None) -> Response:
        return self._request("POST", path, json)

    def put(self, path: str, json: Dict[str, Any] | None = None) -> Response:
        return self._request("PUT", path, json)

    def delete(self, path: str) -> Response:
        return self._request("DELETE", path)


__all__ = ["TestClient", "status"]
