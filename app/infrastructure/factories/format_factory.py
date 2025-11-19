"""Factory responsible for selecting catalog format strategies."""

from __future__ import annotations

from typing import Dict, Type

from ..formats.base import CatalogFormatStrategy
from ..formats.json_format import JsonFormatStrategy
from ..formats.xml_format import XmlFormatStrategy


class FormatFactory:
    """Return the appropriate strategy for the requested format."""

    _strategies: Dict[str, Type[CatalogFormatStrategy]] = {
        "json": JsonFormatStrategy,
        "xml": XmlFormatStrategy,
    }

    def create(self, fmt: str) -> CatalogFormatStrategy:
        key = fmt.lower()
        if key not in self._strategies:
            raise ValueError(f"Unsupported format: {fmt}")
        return self._strategies[key]()
