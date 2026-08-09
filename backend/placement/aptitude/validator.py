"""
Aptitude Validator
"""

from typing import Dict, Any
from placement.aptitude.schemas import AptitudeOutput


class AptitudeValidator:
    """
    Validates aptitude answers and calculates scores.
    """

    @staticmethod
    def validate_answer(question: Dict[str, Any], answer: str) -> Dict[str, Any]:
        is_correct = answer == question.get("correct_answer", "")
        return {
            "is_correct": is_correct,
            "correct_answer": question.get("correct_answer", ""),
            "score": 1.0 if is_correct else 0.0
        }
