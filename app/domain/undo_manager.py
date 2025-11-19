"""Undo manager implementing the Memento pattern with a bounded history."""

from __future__ import annotations

from collections import deque
from typing import Deque

from .catalog import Catalog
from .memento import CatalogMemento


class UndoManager:
    """Maintains the last N catalog states to support undo."""

    def __init__(self, limit: int = 10) -> None:
        self._history: Deque[CatalogMemento] = deque(maxlen=limit)

    def record_state(self, memento: CatalogMemento) -> None:
        """Append a new snapshot to the history."""

        self._history.append(memento)

    def undo(self, catalog: Catalog) -> None:
        """Restore the catalog to the most recent snapshot."""

        if not self._history:
            raise ValueError("No states available to undo")
        catalog.restore(self._history.pop())

    def can_undo(self) -> bool:
        """Return ``True`` when an undo action is possible."""

        return bool(self._history)

    def remaining(self) -> int:
        """Return the number of states still stored."""

        return len(self._history)
