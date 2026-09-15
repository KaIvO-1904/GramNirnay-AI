import pytest
import json
from backend.structured_output import StructuredOutputHandler
from pydantic import BaseModel

class TestSchema(BaseModel):
    text: str
    items: list[str]

def test_json_repair_apostrophe():
    # Test the specific failure: Employees' Provident Fund with invalid escape \'
    malformed_json = '{"text": "Employees\' Provident Fund", "items": ["Item 1", "Item 2"]}'

    # The repair_json should handle it
    repaired = StructuredOutputHandler.repair_json(malformed_json)
    assert "\\'" not in repaired

    # And validate_and_parse should succeed
    parsed = StructuredOutputHandler.validate_and_parse(malformed_json, TestSchema)
    assert parsed is not None
    assert parsed.text == "Employees' Provident Fund"

def test_json_repair_trailing_comma():
    malformed_json = '{"text": "test", "items": ["a", "b",],}'
    parsed = StructuredOutputHandler.validate_and_parse(malformed_json, TestSchema)
    assert parsed is not None
    assert parsed.items == ["a", "b"]

def test_json_unicode_and_symbols():
    json_text = '{"text": "Price: ₹100", "items": ["Item 1", "Item 2"]}'
    parsed = StructuredOutputHandler.validate_and_parse(json_text, TestSchema)
    assert parsed is not None
    assert "₹" in parsed.text
