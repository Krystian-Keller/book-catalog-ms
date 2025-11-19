"""Memento objects capturing immutable snapshots of the catalog."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .book import Book


@dataclass(frozen=True)
class CatalogMemento:
    """Stores a deep copy of the catalog state for undo operations."""

    state: Dict[str, Book]
