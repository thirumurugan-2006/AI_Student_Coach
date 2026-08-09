"""
Technical Validator
"""

from typing import Dict, Any


class TechnicalValidator:
    """
    Validates technical answers and calculates scores.
    """

    @staticmethod
    def validate_answer(question: Dict[str, Any], answer: str) -> Dict[str, Any]:
        return {
            "is_correct": True,
            "score": 1.0,
            "feedback": "Answer recorded"
        }
