"""
Placement Evaluator

Evaluates placement round results and updates career intelligence.
"""

from typing import Dict, Any
from core.logger import logger


class PlacementEvaluator:
    """
    Evaluates placement round results.
    """

    def __init__(self, memory):
        self.memory = memory

    def evaluate_round(self, student_id: str, round_type: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a placement round result.

        Args:
            student_id: The student's ID
            round_type: Type of round (aptitude, coding, technical, interview, hr)
            result: The raw result from the skill

        Returns:
            Evaluation result with score, strengths, weaknesses
        """
        logger.info(f"Evaluating placement round '{round_type}' for student {student_id}")

        evaluators = {
            "aptitude": self._evaluate_aptitude,
            "coding": self._evaluate_coding,
            "technical": self._evaluate_technical,
            "interview": self._evaluate_interview,
            "hr": self._evaluate_hr,
        }

        evaluator = evaluators.get(round_type, self._evaluate_default)
        eval_result = evaluator(result)

        # Update student memory with placement evidence
        self._update_career_intelligence(student_id, round_type, eval_result)

        return eval_result

    def _evaluate_aptitude(self, result: Dict[str, Any]) -> Dict[str, Any]:
        score = 100.0  # Placeholder - will be updated when answer is submitted
        return {
            "score": score,
            "strengths": ["Aptitude skills"],
            "weaknesses": [],
            "topics": ["logical_reasoning"],
            "difficulty": "medium",
            "performance": "good",
            "feedback": "Aptitude round completed"
        }

    def _evaluate_coding(self, result: Dict[str, Any]) -> Dict[str, Any]:
        evaluation = result.get("evaluation", {})
        score = evaluation.get("score", 0.0)
        return {
            "score": score,
            "strengths": ["Coding skills"] if score >= 50 else [],
            "weaknesses": ["Problem solving"] if score < 50 else [],
            "topics": ["data_structures", "algorithms"],
            "difficulty": "medium",
            "performance": "good" if score >= 50 else "needs_improvement",
            "feedback": evaluation.get("feedback", "Coding round completed")
        }

    def _evaluate_technical(self, result: Dict[str, Any]) -> Dict[str, Any]:
        score = 80.0  # Placeholder
        return {
            "score": score,
            "strengths": ["Technical knowledge"],
            "weaknesses": [],
            "topics": result.get("question", {}).get("topic", "general"),
            "difficulty": "medium",
            "performance": "good",
            "feedback": "Technical round completed"
        }

    def _evaluate_interview(self, result: Dict[str, Any]) -> Dict[str, Any]:
        score = 75.0  # Placeholder
        return {
            "score": score,
            "strengths": ["Communication"],
            "weaknesses": [],
            "topics": ["interview_skills"],
            "difficulty": "medium",
            "performance": "good",
            "feedback": "Interview round completed"
        }

    def _evaluate_hr(self, result: Dict[str, Any]) -> Dict[str, Any]:
        score = 80.0  # Placeholder
        return {
            "score": score,
            "strengths": ["Soft skills"],
            "weaknesses": [],
            "topics": ["hr_skills"],
            "difficulty": "medium",
            "performance": "good",
            "feedback": "HR round completed"
        }

    def _evaluate_default(self, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "score": 50.0,
            "strengths": [],
            "weaknesses": [],
            "topics": [],
            "difficulty": "medium",
            "performance": "average",
            "feedback": "Round completed"
        }

    def evaluate_answer(self, student_id: str, round_type: str, answer: Any) -> Dict[str, Any]:
        """
        Evaluate a specific answer within a round.
        """
        logger.info(f"Evaluating answer for round '{round_type}' for student {student_id}")

        if round_type == "aptitude":
            from placement.aptitude.validator import AptitudeValidator
            # This would need the current question context
            return {"score": 0.0, "feedback": "Answer recorded"}

        if round_type == "coding":
            return {
                "score": 0.0,
                "feedback": "Code submitted for evaluation"
            }

        return {
            "score": 50.0,
            "feedback": "Answer recorded"
        }

    def _update_career_intelligence(self, student_id: str, round_type: str, eval_result: Dict[str, Any]):
        """
        Update student memory with placement evidence.
        """
        profile = self.memory.get_profile(student_id)
        if not profile:
            return

        # Add placement evidence to interview history
        evidence = {
            "round_type": round_type,
            "score": eval_result.get("score", 0),
            "topics": eval_result.get("topics", []),
            "timestamp": str(__import__("datetime").datetime.now())
        }

        if "placement_history" not in profile:
            profile["placement_history"] = []

        profile["placement_history"].append(evidence)

        # Update readiness score based on placement performance
        placement_scores = [e.get("score", 0) for e in profile.get("placement_history", [])]
        if placement_scores:
            avg_score = sum(placement_scores) / len(placement_scores)
            # Blend with existing readiness score
            current_readiness = profile.get("readiness_score", 0)
            profile["readiness_score"] = round((current_readiness + avg_score) / 2, 2)
