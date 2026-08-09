"""
Readiness Gate Service

Determines when a student is ready to transition from Career Preparation
to Placement Simulation based on assessment, learning, and skill data.
"""

from typing import Dict, Any, Optional, List
from core.logger import logger


class ReadinessGate:
    """
    Readiness Gate evaluates student readiness for placement simulation.
    
    Uses assessment results, learning progress, and skill mastery to determine
    if a student should proceed to placement simulation or continue learning.
    """

    def __init__(self):
        pass

    READINESS_THRESHOLD = 70.0  # Minimum score to be considered ready
    MIN_LEARNING_PROGRESS = 60.0  # Minimum learning progress
    MIN_SKILL_MASTERY_COUNT = 3  # Minimum number of mastered skills

    def evaluate_readiness(
        self,
        student_id: str,
        skill_mastery: Dict[str, Dict[str, Any]],
        learning_progress: float,
        assessment_scores: Dict[str, float],
        career_goal: Optional[str] = None,
        target_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate if student is ready for placement simulation.
        
        Args:
            student_id: The student's ID
            skill_mastery: Dictionary of skill mastery levels
            learning_progress: Overall learning progress (0-100)
            assessment_scores: Dictionary of assessment scores by skill
            career_goal: Student's career goal
            target_role: Student's target role
            
        Returns:
            Readiness evaluation with decision and recommendations
        """
        # Count mastered skills
        mastered_skills = [
            skill for skill, data in skill_mastery.items()
            if data.get("mastery_level") == "mastered"
        ]
        
        # Calculate average assessment score
        if assessment_scores:
            avg_assessment_score = sum(assessment_scores.values()) / len(assessment_scores)
        else:
            avg_assessment_score = 0.0
        
        # Calculate overall readiness score
        readiness_score = self._calculate_readiness_score(
            skill_mastery, learning_progress, assessment_scores
        )
        
        # Determine readiness status
        is_ready = self._is_ready(
            readiness_score,
            len(mastered_skills),
            learning_progress,
            avg_assessment_score
        )
        
        # Generate recommendations
        if is_ready:
            next_action = "placement_simulation"
            recommendations = [
                "You are ready for placement simulation!",
                "Practice with placement-style questions",
                "Review technical interview topics",
                "Prepare behavioral interview responses"
            ]
        else:
            next_action = "continue_learning"
            recommendations = self._generate_learning_recommendations(
                skill_mastery, learning_progress, assessment_scores, career_goal, target_role
            )
        
        return {
            "student_id": student_id,
            "is_ready": is_ready,
            "readiness_score": readiness_score,
            "next_action": next_action,
            "mastered_skills_count": len(mastered_skills),
            "mastered_skills": mastered_skills,
            "learning_progress": learning_progress,
            "average_assessment_score": avg_assessment_score,
            "recommendations": recommendations,
            "breakdown": {
                "skills": len(mastered_skills),
                "learning": learning_progress,
                "assessments": avg_assessment_score
            }
        }

    def _calculate_readiness_score(
        self,
        skill_mastery: Dict[str, Dict[str, Any]],
        learning_progress: float,
        assessment_scores: Dict[str, float]
    ) -> float:
        """Calculate overall readiness score."""
        # Skill mastery component (40%)
        if skill_mastery:
            mastery_scores = []
            for skill, data in skill_mastery.items():
                mastery_level = data.get("mastery_level", "needs_improvement")
                if mastery_level == "mastered":
                    mastery_scores.append(100)
                elif mastery_level == "learning":
                    mastery_scores.append(60)
                else:
                    mastery_scores.append(30)
            skills_score = sum(mastery_scores) / len(mastery_scores) if mastery_scores else 0.0
        else:
            skills_score = 0.0
        
        # Learning progress component (30%)
        learning_score = learning_progress
        
        # Assessment scores component (30%)
        if assessment_scores:
            assessment_score = sum(assessment_scores.values()) / len(assessment_scores)
        else:
            assessment_score = 0.0
        
        # Weighted average
        readiness_score = (
            skills_score * 0.4 +
            learning_score * 0.3 +
            assessment_score * 0.3
        )
        
        return readiness_score

    def _is_ready(
        self,
        readiness_score: float,
        mastered_skills_count: int,
        learning_progress: float,
        avg_assessment_score: float
    ) -> bool:
        """Determine if student meets readiness criteria."""
        return (
            readiness_score >= self.READINESS_THRESHOLD and
            mastered_skills_count >= self.MIN_SKILL_MASTERY_COUNT and
            learning_progress >= self.MIN_LEARNING_PROGRESS and
            avg_assessment_score >= 60.0
        )

    def _generate_learning_recommendations(
        self,
        skill_mastery: Dict[str, Dict[str, Any]],
        learning_progress: float,
        assessment_scores: Dict[str, float],
        career_goal: Optional[str],
        target_role: Optional[str]
    ) -> List[str]:
        """Generate recommendations for students not yet ready."""
        recommendations = []
        
        # Check skill gaps
        weak_skills = [
            skill for skill, data in skill_mastery.items()
            if data.get("mastery_level") == "needs_improvement"
        ]
        
        if weak_skills:
            recommendations.append(f"Focus on improving: {', '.join(weak_skills[:3])}")
        
        # Check learning progress
        if learning_progress < self.MIN_LEARNING_PROGRESS:
            recommendations.append("Complete more learning modules to increase progress")
        
        # Check assessment scores
        if assessment_scores:
            low_assessment_skills = [
                skill for skill, score in assessment_scores.items()
                if score < 60.0
            ]
            if low_assessment_skills:
                recommendations.append(f"Retake assessments for: {', '.join(low_assessment_skills[:3])}")
        
        # Career-specific recommendations
        if career_goal or target_role:
            recommendations.append("Practice problems relevant to your target role")
        
        # General recommendation
        recommendations.append("Continue building your skill foundation before placement simulation")
        
        return recommendations

    def get_readiness_status(self, readiness_score: float) -> str:
        """Get human-readable readiness status."""
        if readiness_score >= 80:
            return "ready"
        elif readiness_score >= 60:
            return "progressing"
        elif readiness_score >= 40:
            return "needs_work"
        else:
            return "starting"
