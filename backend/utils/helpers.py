"""
General Utility Helpers.

Reusable helper functions used across the backend.
"""

import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# String Helpers
# ---------------------------------------------------------------------------

def generate_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def slugify(text: str) -> str:
    """
    Convert a string to a URL-safe slug.

    Example:
        'Hello World!' → 'hello-world'
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to max_length characters.

    Args:
        text: Input string.
        max_length: Maximum allowed length including suffix.
        suffix: String appended when truncation occurs.

    Returns:
        Truncated string.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def sanitise_email(email: str) -> str:
    """Lowercase and strip whitespace from an email address."""
    return email.lower().strip()


def is_valid_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


# ---------------------------------------------------------------------------
# Date / Time Helpers
# ---------------------------------------------------------------------------

def utcnow() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def utcnow_iso() -> str:
    """Return the current UTC datetime as an ISO 8601 string."""
    return utcnow().isoformat()


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    Format a datetime object to ISO 8601 string.

    Args:
        dt: Datetime object or None.

    Returns:
        ISO 8601 string or None.
    """
    if dt is None:
        return None
    return dt.isoformat()


# ---------------------------------------------------------------------------
# Collection Helpers
# ---------------------------------------------------------------------------

def deduplicate(items: List[Any]) -> List[Any]:
    """
    Remove duplicates from a list while preserving order.

    Args:
        items: Input list with potential duplicates.

    Returns:
        List with duplicates removed.
    """
    seen = set()
    result = []
    for item in items:
        key = str(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def flatten_dict(
    d: Dict[str, Any], parent_key: str = "", sep: str = "."
) -> Dict[str, Any]:
    """
    Flatten a nested dictionary with dot-notation keys.

    Example:
        {"a": {"b": 1}} → {"a.b": 1}
    """
    items: Dict[str, Any] = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Safely retrieve a nested value from a dictionary.

    Args:
        data: The dictionary to search.
        *keys: Sequence of keys for nested access.
        default: Value to return if any key is missing.

    Returns:
        The value at the nested path, or default.
    """
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current


# ---------------------------------------------------------------------------
# Score / Metric Helpers
# ---------------------------------------------------------------------------

def clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """
    Clamp a float value between min_val and max_val.

    Args:
        value: Input value.
        min_val: Minimum allowed value.
        max_val: Maximum allowed value.

    Returns:
        Clamped value.
    """
    return max(min_val, min(max_val, value))


def percentage(part: float, total: float) -> float:
    """
    Calculate a safe percentage.

    Args:
        part: Numerator.
        total: Denominator.

    Returns:
        Percentage (0–100), or 0 if total is 0.
    """
    if total == 0:
        return 0.0
    return clamp((part / total) * 100)


def average(values: List[float]) -> float:
    """
    Calculate the arithmetic mean of a list of floats.

    Args:
        values: List of numeric values.

    Returns:
        Average value, or 0 if list is empty.
    """
    if not values:
        return 0.0
    return sum(values) / len(values)
