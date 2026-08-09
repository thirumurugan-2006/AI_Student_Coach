"""
Helper functions for common operations across the application.
"""

from typing import Optional


def normalize_text(text: Optional[str]) -> str:
    """
    Safely normalize text by handling None, empty strings, and whitespace.
    
    Args:
        text: Input text that may be None or contain whitespace.
        
    Returns:
        Normalized lowercase string, or empty string if input is None/empty.
        
    Examples:
        None → ""
        "" → ""
        " Backend Developer " → "backend developer"
        "  " → ""
    """
    if text is None:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    return text.strip().lower()


def safe_get(data: dict, key: str, default=None):
    """
    Safely get a value from a dictionary, returning default if key is missing.
    
    Args:
        data: Dictionary to get value from.
        key: Key to retrieve.
        default: Default value if key is missing.
        
    Returns:
        Value from dictionary or default.
    """
    if data is None:
        return default
    return data.get(key, default)
