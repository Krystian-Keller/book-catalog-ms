"""Tests ensuring the serialization strategies behave correctly."""

import json
import xml.etree.ElementTree as ET

import pytest

from app.infrastructure.factories.format_factory import FormatFactory
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


def test_json_strategy_invalid_input() -> None:
    strategy = JsonFormatStrategy()

    with pytest.raises(json.JSONDecodeError):
        strategy.deserialize("{invalid}")



def test_xml_strategy_invalid_input() -> None:
    strategy = XmlFormatStrategy()

    with pytest.raises(ET.ParseError):
        strategy.deserialize("<catalog><book></catalog>")



def test_format_factory_unsupported_format() -> None:
    factory = FormatFactory()

    with pytest.raises(ValueError):
        factory.create("yaml")
