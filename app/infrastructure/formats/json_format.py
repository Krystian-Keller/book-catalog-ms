"""JSON format strategy built on the standard library."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from .base import CatalogFormatStrategy


class JsonFormatStrategy(CatalogFormatStrategy):
    """Serialize the catalog to a JSON document."""

    def serialize(self, books: List[Dict[str, Any]]) -> str:
        return json.dumps({"catalog": books}, indent=2)

    def deserialize(self, content: str) -> List[Dict[str, Any]]:
        if not content.strip():
            return []
        parsed = json.loads(content)
        return list(parsed.get("catalog", []))
