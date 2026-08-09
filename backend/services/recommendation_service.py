"""
Recommendation Service.

Generates personalised career recommendations based on the student's
current profile, knowledge graph, and readiness score stored in memory.

Recommendations cover:
- Skill gaps to close
- Next learning topics
- Interview preparation areas
- Career path options
"""

from typing import Dict, Any, List

from memory.student_memory import StudentMemory
from core.constants import (
    READINESS_READY_THRESHOLD,
    READINESS_PROGRESSING_THRESHOLD,
    READINESS_STATUS_READY,
    READINESS_STATUS_PROGRESSING,
    READINESS_STATUS_NEEDS_WORK,
    READINESS_STATUS_STARTING,
)
from core.logger import logger
from core.helpers import normalize_text


class RecommendationService:
    """
    Rule-based recommendation engine.

    Analyses the student's in-memory profile and produces actionable
    recommendations without requiring an LLM call — keeping it fast and
    deterministic.
    """

    def __init__(self, memory: StudentMemory):
        self.memory = memory

    def get_recommendations(self, student_id: str) -> Dict[str, Any]:
        """
        Generate a full recommendation bundle for a student.

        Args:
            student_id: The student's ID.

        Returns:
            Dictionary containing categorised recommendations.
        """
        profile = self.memory.get_profile(student_id)
        if not profile:
            logger.warning(f"No profile found for student {student_id}")
            return self._empty_recommendations()

        readiness = profile.get("readiness_score", 0.0)
        status = self._get_readiness_status(readiness)

        return {
            "student_id": student_id,
            "readiness_score": readiness,
            "readiness_status": status,
            "skill_gap_recommendations": self._recommend_skill_gaps(profile),
            "learning_recommendations": self._recommend_learning_topics(profile),
            "interview_recommendations": self._recommend_interview_prep(profile),
            "career_path_options": self._recommend_career_paths(profile),
            "priority_action": self._get_priority_action(profile, status),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_readiness_status(self, score: float) -> str:
        if score >= READINESS_READY_THRESHOLD:
            return READINESS_STATUS_READY
        if score >= READINESS_PROGRESSING_THRESHOLD:
            return READINESS_STATUS_PROGRESSING
        if score >= READINESS_READY_THRESHOLD / 3:
            return READINESS_STATUS_NEEDS_WORK
        return READINESS_STATUS_STARTING

    def _recommend_skill_gaps(self, profile: Dict) -> List[str]:
        """Identify skills below 60% proficiency."""
        skills: Dict[str, float] = profile.get("skills", {})
        gaps = [skill for skill, score in skills.items() if score < 60.0]
        return gaps[:5]  # Top 5 gaps

    def _recommend_learning_topics(self, profile: Dict) -> List[str]:
        """Recommend topics from the roadmap not yet completed."""
        roadmap: List[str] = profile.get("roadmap", [])
        completed: List[str] = profile.get("completed_topics", [])
        weak: List[str] = profile.get("weak_topics", [])

        pending = [t for t in roadmap if t not in completed]

        # Prioritise weak topics first
        prioritised = [t for t in pending if t in weak]
        remaining = [t for t in pending if t not in weak]

        return (prioritised + remaining)[:5]

    def _recommend_interview_prep(self, profile: Dict) -> List[str]:
        """Suggest interview areas based on weak topics and interview history."""
        weak_topics: List[str] = profile.get("weak_topics", [])
        interview_history: List[Dict] = profile.get("interview_history", [])

        recommendations: List[str] = []

        if not interview_history:
            recommendations.append("Complete your first mock interview to identify weaknesses")

        for topic in weak_topics[:3]:
            recommendations.append(f"Practice interview questions on: {topic}")

        if len(interview_history) > 0:
            latest = interview_history[-1]
            score = latest.get("overall_score", 0)
            if score < 60:
                recommendations.append("Review STAR method for behavioural questions")
                recommendations.append("Practice system design fundamentals")

        return recommendations or ["Start with a mock interview session"]

    def _recommend_career_paths(self, profile: Dict) -> List[str]:
        """Suggest career paths based on the student's goal and skills."""
        goal: str = normalize_text(profile.get("career_goal", ""))
        experience: str = normalize_text(profile.get("experience_level", "beginner"))
        skills_str = normalize_text(str(profile.get("skills", {})))

        paths: List[str] = []

        if "backend" in goal or "backend" in skills_str:
            paths.append("Backend Software Engineer")
            paths.append("API / Platform Engineer")

        if "frontend" in goal:
            paths.append("Frontend Engineer")
            paths.append("Full-Stack Engineer")

        if "data" in goal or "ml" in goal:
            paths.append("Data Engineer")
            paths.append("Machine Learning Engineer")

        if not paths:
            paths = ["Software Engineer", "Full-Stack Developer", "DevOps Engineer"]

        return paths[:3]

    def _get_priority_action(self, profile: Dict, status: str) -> str:
        """Determine the single most important action for the student right now."""
        if not profile.get("survey_completed"):
            return "Complete the career discovery survey to personalise your roadmap"
        if not profile.get("assessment_completed"):
            return "Run a skills assessment to identify your knowledge gaps"
        if status == READINESS_STATUS_STARTING:
            return "Begin your learning roadmap with the first recommended topic"
        if status == READINESS_STATUS_NEEDS_WORK:
            weak = profile.get("weak_topics", [])
            if weak:
                return f"Focus on strengthening: {weak[0]}"
        if status == READINESS_STATUS_PROGRESSING:
            return "Complete a mock interview to prepare for real interviews"
        if status == READINESS_STATUS_READY:
            return "You are job-ready! Start applying to your target companies"
        return "Continue building your skills and complete your roadmap"

    def _empty_recommendations(self) -> Dict[str, Any]:
        return {
            "student_id": None,
            "readiness_score": 0,
            "readiness_status": READINESS_STATUS_STARTING,
            "skill_gap_recommendations": [],
            "learning_recommendations": [],
            "interview_recommendations": ["Complete the career survey first"],
            "career_path_options": [],
            "priority_action": "Create your profile by completing the career survey",
        }
