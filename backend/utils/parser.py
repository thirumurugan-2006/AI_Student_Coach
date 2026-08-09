"""
Parser Utilities.

Parsing helpers for LLM outputs, student profile data,
and general text transformation.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from utils.json_utils import parse_llm_json, safe_loads


# ---------------------------------------------------------------------------
# LLM Output Parsers
# ---------------------------------------------------------------------------

def parse_skill_result(raw: Any, schema_class=None) -> Dict[str, Any]:
    """
    Parse a raw skill result from the LLM into a dictionary.

    Handles three possible input types:
    - Pydantic model instance → model_dump()
    - String → JSON parse with markdown stripping
    - Dict → returned as-is

    Args:
        raw: Raw result from LLM Interface.
        schema_class: Optional Pydantic class for validation (unused if already model).

    Returns:
        Dictionary representation of the result.
    """
    if raw is None:
        return {}

    # Already a Pydantic model
    if hasattr(raw, "model_dump"):
        return raw.model_dump()

    # String — try JSON parse
    if isinstance(raw, str):
        parsed = parse_llm_json(raw, default={})
        return parsed if isinstance(parsed, dict) else {"raw_response": raw}

    # Already a dict
    if isinstance(raw, dict):
        return raw

    return {"raw_response": str(raw)}


def parse_confidence_level(text: str) -> float:
    """
    Convert a text confidence level to a numeric score.

    Handles common LLM confidence expression patterns.

    Args:
        text: Confidence expression (e.g. "high", "medium", "75%", "0.8").

    Returns:
        Numeric confidence score 0–100.
    """
    text = text.lower().strip()

    # Numeric percentage
    pct_match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    if pct_match:
        return min(100.0, float(pct_match.group(1)))

    # Decimal fraction
    dec_match = re.search(r"^0\.\d+$", text)
    if dec_match:
        return float(text) * 100

    # Text levels
    level_map = {
        "very high": 90.0,
        "high": 75.0,
        "medium": 50.0,
        "moderate": 50.0,
        "low": 25.0,
        "very low": 10.0,
        "none": 0.0,
    }
    for label, score in level_map.items():
        if label in text:
            return score

    # Plain integer
    int_match = re.search(r"(\d+)", text)
    if int_match:
        return min(100.0, float(int_match.group(1)))

    return 50.0  # Default


def parse_difficulty_level(text: str) -> str:
    """
    Normalise a difficulty string to one of: easy, medium, hard.

    Args:
        text: Raw difficulty string from LLM.

    Returns:
        Normalised difficulty string.
    """
    text = text.lower().strip()
    if text in ("easy", "beginner", "simple", "basic"):
        return "easy"
    if text in ("hard", "difficult", "advanced", "expert", "challenging"):
        return "hard"
    return "medium"


# ---------------------------------------------------------------------------
# Profile Data Parsers
# ---------------------------------------------------------------------------

def parse_skills_list(raw_skills: Any) -> List[str]:
    """
    Normalise a skills value to a clean list of strings.

    Handles: list, comma-separated string, single string.

    Args:
        raw_skills: Skills data in any format.

    Returns:
        List of clean skill name strings.
    """
    if isinstance(raw_skills, list):
        return [str(s).strip() for s in raw_skills if s]

    if isinstance(raw_skills, str):
        # Comma or newline separated
        items = re.split(r"[,\n;]+", raw_skills)
        return [i.strip() for i in items if i.strip()]

    return []


def parse_roadmap(raw: Any) -> List[str]:
    """
    Parse a roadmap value into a list of topic strings.

    Args:
        raw: Roadmap data — list, JSON string, or plain string.

    Returns:
        List of topic strings.
    """
    if isinstance(raw, list):
        return [str(t).strip() for t in raw if t]

    if isinstance(raw, str):
        # Try JSON array first
        parsed = safe_loads(raw)
        if isinstance(parsed, list):
            return [str(t).strip() for t in parsed if t]
        # Fallback: split on newlines
        return [line.strip() for line in raw.split("\n") if line.strip()]

    return []


def parse_experience_level(raw: str) -> str:
    """
    Normalise an experience level string.

    Args:
        raw: Raw experience level from LLM or user input.

    Returns:
        One of: beginner, intermediate, advanced, expert.
    """
    raw = raw.lower().strip()

    if any(w in raw for w in ["beginner", "fresh", "junior", "new", "student", "entry"]):
        return "beginner"
    if any(w in raw for w in ["intermediate", "mid", "some experience"]):
        return "intermediate"
    if any(w in raw for w in ["advanced", "senior", "experienced", "lead"]):
        return "advanced"
    if any(w in raw for w in ["expert", "principal", "architect", "staff"]):
        return "expert"

    return "beginner"


# ---------------------------------------------------------------------------
# Text Parsers
# ---------------------------------------------------------------------------

def extract_topics_from_text(text: str) -> List[str]:
    """
    Extract a list of topics or keywords from unstructured text.

    Uses capitalised words and noun-phrase detection heuristics.

    Args:
        text: Unstructured text to parse.

    Returns:
        List of extracted topic strings.
    """
    # Find capitalised words and phrases
    matches = re.findall(r"\b[A-Z][a-zA-Z0-9+#.]*(?:\s+[A-Z][a-zA-Z0-9+#.]*)*\b", text)
    # Filter common stop words and short tokens
    stop = {"The", "A", "An", "In", "On", "At", "To", "For", "Of", "And", "Or", "I"}
    topics = [m for m in matches if m not in stop and len(m) > 2]
    return list(dict.fromkeys(topics))  # Deduplicate preserving order


def clean_llm_text(text: str) -> str:
    """
    Remove common LLM formatting artifacts from a text string.

    Strips: markdown bold, italic, headers, and excessive whitespace.

    Args:
        text: Raw LLM text.

    Returns:
        Cleaned plain text.
    """
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)   # Bold
    text = re.sub(r"\*(.+?)\*", r"\1", text)         # Italic
    text = re.sub(r"#{1,6}\s+", "", text)             # Headers
    text = re.sub(r"```[\w]*\n?", "", text)           # Code fences
    text = re.sub(r"`(.+?)`", r"\1", text)            # Inline code
    text = re.sub(r"\n{3,}", "\n\n", text)            # Excessive newlines
    return text.strip()
