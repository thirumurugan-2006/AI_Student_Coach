"""
Placement Report Generator

Generates the final placement report after all rounds are completed.
"""

from typing import Dict, Any, List
from core.logger import logger
from placement.report.schemas import PlacementReport, RoundScore
from placement.evaluator.scoring import PlacementScoring


class PlacementReportGenerator:
    """
    Generates the final placement report.
    """

    def __init__(self, memory, llm):
        self.memory = memory
        self.llm = llm
        self.scoring = PlacementScoring()

    async def generate(self, student_id: str) -> Dict[str, Any]:
        """
        Generate a final placement report for a student.

        Args:
            student_id: The student's ID

        Returns:
            Placement report dictionary
        """
        logger.info(f"Generating placement report for student {student_id}")

        profile = self.memory.get_profile(student_id)
        if not profile:
            return {"error": "Student profile not found"}

        placement_history = profile.get("placement_history", [])
        round_results = self._organize_round_results(placement_history)

        overall_score = self.scoring.calculate_overall_score(round_results)

        # Use LLM to generate personalized recommendations
        recommendations = await self._generate_recommendations(student_id, overall_score, round_results)

        report = PlacementReport(
            student_id=student_id,
            overall_score=overall_score,
            round_scores=[
                RoundScore(
                    round_type=round_type,
                    score=result.get("score", 0),
                    feedback=result.get("feedback", "")
                )
                for round_type, result in round_results.items()
            ],
            strengths=recommendations.get("strengths", []),
            weaknesses=recommendations.get("weaknesses", []),
            recommendations=recommendations.get("recommendations", []),
            next_best_action=recommendations.get("next_best_action", "Continue learning"),
            readiness_update=overall_score
        )

        logger.info(f"Placement report generated for student {student_id}: score={overall_score}")
        return report.model_dump()

    def _organize_round_results(self, placement_history: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Organize placement history by round type.
        """
        round_results = {}
        for entry in placement_history:
            round_type = entry.get("round_type")
            if round_type:
                round_results[round_type] = entry
        return round_results

    async def _generate_recommendations(self, student_id: str, overall_score: float, round_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use LLM to generate personalized recommendations.
        """
        profile = self.memory.get_profile(student_id)
        if not profile:
            return {
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
                "next_best_action": "Continue learning"
            }

        # For now, return rule-based recommendations
        # In a full implementation, this would call the LLM
        strengths = []
        weaknesses = []
        recommendations = []

        for round_type, result in round_results.items():
            score = result.get("score", 0)
            if score >= 70:
                strengths.append(f"Strong performance in {round_type}")
            elif score < 50:
                weaknesses.append(f"Needs improvement in {round_type}")
                recommendations.append(f"Focus more on {round_type} practice")

        if overall_score >= 75:
            next_best_action = "Ready for real interviews"
        elif overall_score >= 50:
            next_best_action = "Continue practicing and improving weak areas"
        else:
            next_best_action = "Go back to learning and strengthen fundamentals"

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "next_best_action": next_best_action
        }
