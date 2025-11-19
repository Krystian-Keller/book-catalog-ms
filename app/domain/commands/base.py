"""Command interface used to implement catalog mutations."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Command(ABC):
    """Defines the operations supported by every command object."""

    @abstractmethod
    def execute(self) -> None:
        """Apply the command action."""

    @abstractmethod
    def undo(self) -> None:
        """Undo the command action."""
