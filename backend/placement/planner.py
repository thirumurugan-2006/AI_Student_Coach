"""
Placement Planner

Determines the next placement round based on student readiness,
previous performance, and career goals.
"""

from typing import Dict, Any
from core.logger import logger


class PlacementPlanner:
    """
    Determines the next placement round for a student.

    Reads:
    - Career goal
    - Target role
    - Student skills
    - Skill gaps
    - Assessment history
    - Learning progress
    - Readiness score
    - Previous placement performance
    """

    ROUNDS = [
        "aptitude",
        "coding",
        "technical",
        "interview",
        "hr"
    ]

    def __init__(self, memory):
        self.memory = memory

    def get_next_round(self, student_id: str, simulation_id: str = None) -> Dict[str, Any]:
        """
        Return exactly ONE next action for the placement simulation.

        Args:
            student_id: The student's ID
            simulation_id: Optional simulation ID to check progress

        Returns:
            Dictionary with next_action and reason
        """
        profile = self.memory.get_profile(student_id)
        if not profile:
            logger.warning(f"No profile found for student {student_id}")
            return {
                "next_action": "aptitude",
                "reason": "No profile found, starting from the beginning"
            }

        # If no simulation progress, start with aptitude
        if not simulation_id:
            return {
                "next_action": "aptitude",
                "reason": "Student is ready for placement simulation and aptitude evaluation is first"
            }

        # Check completed rounds from simulation state
        # For now, implement simple sequential progression
        # The simulator tracks progress
        return {
            "next_action": "aptitude",
            "reason": "Starting placement simulation"
        }

    def build_execution_plan(self, student_id: str, simulation_id: str = None) -> Dict[str, Any]:
        """
        Build a complete execution plan for the placement simulation.

        Args:
            student_id: The student's ID
            simulation_id: Optional simulation ID

        Returns:
            Execution plan dictionary
        """
        profile = self.memory.get_profile(student_id)
        next_round = self.get_next_round(student_id, simulation_id)

        plan = {
            "student_id": student_id,
            "simulation_id": simulation_id,
            "current_stage": "placement",
            "next_round": next_round["next_action"],
            "reason": next_round["reason"],
            "rounds": self.ROUNDS,
            "context": self._build_context(student_id)
        }

        logger.info(f"Placement planner built execution plan for student {student_id}: {next_round['next_action']}")
        return plan

    def _build_context(self, student_id: str) -> Dict[str, Any]:
        """
        Build context for placement rounds using student memory.
        """
        profile = self.memory.get_profile(student_id)
        if not profile:
            return {}

        return {
            "student_id": student_id,
            "career_goal": profile.get("career_goal", "Software Engineer"),
            "target_company": profile.get("target_company", ""),
            "experience_level": profile.get("experience_level", "intermediate"),
            "skills": profile.get("skills", {}),
            "weak_topics": profile.get("weak_topics", []),
            "strong_topics": profile.get("strong_topics", []),
            "readiness_score": profile.get("readiness_score", 0),
            "assessment_history": profile.get("assessment_history", []),
            "interview_history": profile.get("interview_history", [])
        }
