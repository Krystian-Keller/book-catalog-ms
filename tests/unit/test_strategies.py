"""Tests ensuring the serialization strategies behave correctly."""

from app.infrastructure.formats.json_format import JsonFormatStrategy
from app.infrastructure.formats.xml_format import XmlFormatStrategy

SAMPLE = [
    {
        "title": "Example",
        "author": "Author",
        "isbn": "123",
        "publisher": "Press",
        "pages": 50,
    }
]


def test_json_strategy_round_trip() -> None:
    strategy = JsonFormatStrategy()
    serialized = strategy.serialize(SAMPLE)
    assert SAMPLE == strategy.deserialize(serialized)


def test_xml_strategy_round_trip() -> None:
    strategy = XmlFormatStrategy()
    serialized = strategy.serialize(SAMPLE)
    assert SAMPLE == strategy.deserialize(serialized)
