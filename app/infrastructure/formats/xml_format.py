"""XML format strategy powered by :mod:`xml.etree.ElementTree`."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any, Dict, List

from .base import CatalogFormatStrategy


class XmlFormatStrategy(CatalogFormatStrategy):
    """Represent the catalog using a basic XML schema."""

    def serialize(self, books: List[Dict[str, Any]]) -> str:
        root = ET.Element("catalog")
        for book in books:
            book_el = ET.SubElement(root, "book")
            for key, value in book.items():
                child = ET.SubElement(book_el, key)
                child.text = str(value)
        return ET.tostring(root, encoding="unicode")

    def deserialize(self, content: str) -> List[Dict[str, Any]]:
        if not content.strip():
            return []
        root = ET.fromstring(content)
        books: List[Dict[str, Any]] = []
        for book_el in root.findall("book"):
            book_data = {child.tag: child.text or "" for child in book_el}
            if "pages" in book_data:
                try:
                    book_data["pages"] = int(book_data["pages"])
                except ValueError:
                    pass
            books.append(book_data)
        return books
