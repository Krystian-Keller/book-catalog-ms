"""Strategy interface for serialization formats."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class CatalogFormatStrategy(ABC):
    """Defines serialization/deserialization hooks."""

    @abstractmethod
    def serialize(self, books: List[Dict[str, Any]]) -> str:
        """Return a textual representation of the catalog."""

    @abstractmethod
    def deserialize(self, content: str) -> List[Dict[str, Any]]:
        """Convert the textual content back into dictionaries."""
