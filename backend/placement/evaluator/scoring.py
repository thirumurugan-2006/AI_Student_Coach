"""
Placement Scoring

Utility functions for calculating placement scores.
"""

from typing import List, Dict, Any


class PlacementScoring:
    """
    Calculates final placement scores from round results.
    """

    @staticmethod
    def calculate_overall_score(round_results: Dict[str, Dict[str, Any]]) -> float:
        """
        Calculate the overall placement score from all round results.

        Args:
            round_results: Dictionary mapping round types to their evaluation results

        Returns:
            Overall score (0-100)
        """
        if not round_results:
            return 0.0

        weights = {
            "aptitude": 0.15,
            "coding": 0.25,
            "technical": 0.25,
            "interview": 0.20,
            "hr": 0.15
        }

        total_score = 0.0
        total_weight = 0.0

        for round_type, result in round_results.items():
            score = result.get("evaluation", {}).get("score", 0.0)
            weight = weights.get(round_type, 0.1)
            total_score += score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return round(total_score / total_weight, 2)

    @staticmethod
    def determine_readiness_status(score: float) -> str:
        """
        Determine readiness status based on score.
        """
        if score >= 75:
            return "job_ready"
        elif score >= 50:
            return "progressing"
        elif score >= 25:
            return "needs_work"
        else:
            return "just_starting"
