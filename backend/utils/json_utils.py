"""
JSON Utilities.

Safe JSON encoding, decoding, extraction, and repair helpers.
Centralises all JSON handling so errors are caught and logged consistently.
"""

import json
import re
from typing import Any, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


# ---------------------------------------------------------------------------
# Safe Encode / Decode
# ---------------------------------------------------------------------------

def safe_dumps(obj: Any, indent: int = None, default: Any = None) -> str:
    """
    Safely serialise an object to a JSON string.

    Args:
        obj: The object to serialise.
        indent: Optional indentation level.
        default: Fallback for non-serialisable types.

    Returns:
        JSON string, or "{}" on failure.
    """
    try:
        return json.dumps(obj, indent=indent, default=default or str, ensure_ascii=False)
    except (TypeError, ValueError):
        return "{}"


def safe_loads(text: str, default: Any = None) -> Any:
    """
    Safely parse a JSON string.

    Args:
        text: JSON string to parse.
        default: Value to return on parse failure.

    Returns:
        Parsed object, or default.
    """
    if not text or not text.strip():
        return default
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# JSON Extraction (from LLM raw text)
# ---------------------------------------------------------------------------

def extract_json_from_text(text: str) -> Optional[str]:
    """
    Extract the first valid JSON object or array from a mixed-content string.

    Useful when the LLM wraps JSON in markdown code fences or adds
    explanatory text around it.

    Args:
        text: Raw text that may contain JSON.

    Returns:
        Raw JSON string, or None if not found.
    """
    # Remove markdown code fences
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```", "", text)

    # Try to find a JSON object
    obj_match = re.search(r"\{.*\}", text, re.DOTALL)
    if obj_match:
        candidate = obj_match.group()
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass

    # Try to find a JSON array
    arr_match = re.search(r"\[.*\]", text, re.DOTALL)
    if arr_match:
        candidate = arr_match.group()
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass

    return None


def parse_llm_json(text: str, default: Any = None) -> Any:
    """
    Parse JSON from LLM output, stripping markdown and extracting the object.

    Args:
        text: Raw LLM response text.
        default: Fallback value if parsing fails.

    Returns:
        Parsed dictionary/list, or default.
    """
    json_str = extract_json_from_text(text)
    if json_str is None:
        return default
    return safe_loads(json_str, default=default)


# ---------------------------------------------------------------------------
# Pydantic Integration
# ---------------------------------------------------------------------------

def parse_to_schema(data: Any, schema: Type[T]) -> Optional[T]:
    """
    Parse and validate data against a Pydantic schema.

    Args:
        data: Input data — string, dict, or already a model instance.
        schema: Pydantic BaseModel class to validate against.

    Returns:
        Validated schema instance, or None on failure.
    """
    try:
        if isinstance(data, schema):
            return data
        if isinstance(data, str):
            # Try direct JSON parse
            parsed = safe_loads(data)
            if parsed is None:
                # Try extraction from mixed text
                parsed = parse_llm_json(data)
            if parsed is None:
                return None
            return schema(**parsed) if isinstance(parsed, dict) else None
        if isinstance(data, dict):
            return schema(**data)
        return schema.model_validate(data)
    except (ValidationError, TypeError, ValueError):
        return None


def model_to_dict(model: BaseModel) -> dict:
    """
    Convert a Pydantic model instance to a plain dictionary.

    Args:
        model: Pydantic model instance.

    Returns:
        Dictionary representation.
    """
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()


# ---------------------------------------------------------------------------
# Merge / Deep Merge
# ---------------------------------------------------------------------------

def deep_merge(base: dict, override: dict) -> dict:
    """
    Deep-merge two dictionaries. Values from `override` take precedence.

    Args:
        base: Base dictionary.
        override: Dictionary whose values override base.

    Returns:
        Merged dictionary (new object, does not mutate inputs).
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
