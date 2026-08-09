"""
Evaluation Engine Service

Separates evaluation logic from LLM generation.
Evaluates student answers, calculates scores, and generates evidence.
"""

from typing import Dict, Any, List, Optional
from core.logger import logger


class EvaluationEngine:
    """
    Evaluation Engine for assessing student responses.
    
    Separated from LLM generation to ensure:
    - Consistent evaluation criteria
    - Score calculation logic
    - Evidence generation
    - Career Intelligence updates
    """

    def __init__(self):
        pass

    def evaluate_mcq_answer(
        self,
        question_id: str,
        selected_option: int,
        correct_option_index: int,
        question_text: str,
        skill: str
    ) -> Dict[str, Any]:
        """
        Evaluate an MCQ answer.
        
        Args:
            question_id: The question's ID
            selected_option: The option selected by the student
            correct_option_index: The index of the correct answer
            question_text: The question text
            skill: The skill/topic being assessed
            
        Returns:
            Evaluation result with score, feedback, and evidence
        """
        is_correct = selected_option == correct_option_index
        
        if is_correct:
            score = 100.0
            feedback = "Correct! Well done."
            strengths = ["Correct answer"]
            weaknesses = []
        else:
            score = 0.0
            feedback = "Incorrect. Review the explanation and try again."
            strengths = []
            weaknesses = ["Incorrect answer"]
        
        return {
            "question_id": question_id,
            "is_correct": is_correct,
            "score": score,
            "feedback": feedback,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "skill": skill,
            "evidence_type": "mcq_assessment"
        }

    def evaluate_text_answer(
        self,
        question_id: str,
        student_answer: str,
        expected_points: List[str],
        question_text: str,
        skill: str
    ) -> Dict[str, Any]:
        """
        Evaluate a text-based answer (technical, interview, HR).
        
        Args:
            question_id: The question's ID
            student_answer: The student's text answer
            expected_points: Key points that should be covered
            question_text: The question text
            skill: The skill/topic being assessed
            
        Returns:
            Evaluation result with score, feedback, and evidence
        """
        # Simple keyword-based evaluation
        # In production, this could use LLM evaluation or more sophisticated NLP
        
        if not student_answer or not student_answer.strip():
            return {
                "question_id": question_id,
                "is_correct": False,
                "score": 0.0,
                "feedback": "No answer provided.",
                "strengths": [],
                "weaknesses": ["No response"],
                "skill": skill,
                "evidence_type": "text_assessment"
            }
        
        student_answer_lower = student_answer.lower()
        covered_points = []
        missed_points = []
        
        for point in expected_points:
            point_lower = point.lower()
            # Check if any significant part of the expected point is in the answer
            if any(word in student_answer_lower for word in point_lower.split() if len(word) > 3):
                covered_points.append(point)
            else:
                missed_points.append(point)
        
        # Calculate score based on coverage
        if expected_points:
            coverage_ratio = len(covered_points) / len(expected_points)
            score = coverage_ratio * 100
        else:
            score = 50.0  # Default score if no expected points
        
        is_correct = score >= 70.0
        
        if is_correct:
            feedback = "Good answer! You covered the key points."
            strengths = covered_points[:2]  # Top 2 strengths
            weaknesses = missed_points[:1] if missed_points else []
        else:
            feedback = "Your answer could be improved. Review the missed points."
            strengths = covered_points[:1] if covered_points else []
            weaknesses = missed_points[:2]
        
        return {
            "question_id": question_id,
            "is_correct": is_correct,
            "score": score,
            "feedback": feedback,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "skill": skill,
            "evidence_type": "text_assessment"
        }

    def calculate_skill_mastery(
        self,
        skill: str,
        recent_scores: List[float],
        total_attempts: int
    ) -> Dict[str, Any]:
        """
        Calculate overall mastery level for a skill.
        
        Args:
            skill: The skill/topic
            recent_scores: List of recent scores (last 10 attempts)
            total_attempts: Total number of attempts
            
        Returns:
            Mastery level and statistics
        """
        if not recent_scores:
            return {
                "skill": skill,
                "mastery_level": "needs_improvement",
                "average_score": 0.0,
                "total_attempts": total_attempts,
                "trend": "no_data"
            }
        
        average_score = sum(recent_scores) / len(recent_scores)
        
        # Determine mastery level
        if average_score >= 80:
            mastery_level = "mastered"
        elif average_score >= 60:
            mastery_level = "learning"
        else:
            mastery_level = "needs_improvement"
        
        # Calculate trend (simple: compare first half to second half)
        if len(recent_scores) >= 4:
            mid = len(recent_scores) // 2
            first_half_avg = sum(recent_scores[:mid]) / mid
            second_half_avg = sum(recent_scores[mid:]) / (len(recent_scores) - mid)
            
            if second_half_avg > first_half_avg + 10:
                trend = "improving"
            elif second_half_avg < first_half_avg - 10:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "skill": skill,
            "mastery_level": mastery_level,
            "average_score": average_score,
            "total_attempts": total_attempts,
            "trend": trend
        }

    def generate_evidence(
        self,
        evaluation: Dict[str, Any],
        student_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate evidence record for Career Intelligence.
        
        Args:
            evaluation: The evaluation result
            student_id: The student's ID
            context: Additional context (career goal, target role, etc.)
            
        Returns:
            Evidence record
        """
        evidence = {
            "student_id": student_id,
            "skill": evaluation.get("skill"),
            "evidence_type": evaluation.get("evidence_type"),
            "score": evaluation.get("score"),
            "is_correct": evaluation.get("is_correct"),
            "strengths": evaluation.get("strengths", []),
            "weaknesses": evaluation.get("weaknesses", []),
            "feedback": evaluation.get("feedback"),
            "question_id": evaluation.get("question_id"),
            "timestamp": None  # Will be set by database
        }
        
        if context:
            evidence["career_goal"] = context.get("career_goal")
            evidence["target_role"] = context.get("target_role")
        
        return evidence

    def calculate_readiness(
        self,
        skill_mastery: Dict[str, Dict[str, Any]],
        learning_progress: float,
        placement_performance: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall readiness score.
        
        Args:
            skill_mastery: Dictionary of skill mastery levels
            learning_progress: Learning progress (0-100)
            placement_performance: Optional placement performance score
            
        Returns:
            Readiness score and breakdown
        """
        if not skill_mastery:
            return {
                "readiness_score": 0.0,
                "readiness_status": "starting",
                "breakdown": {
                    "skills": 0.0,
                    "learning": learning_progress,
                    "placement": 0.0
                }
            }
        
        # Calculate average skill mastery
        mastery_scores = []
        for skill, data in skill_mastery.items():
            mastery_level = data.get("mastery_level", "needs_improvement")
            if mastery_level == "mastered":
                mastery_scores.append(100)
            elif mastery_level == "learning":
                mastery_scores.append(60)
            else:
                mastery_scores.append(30)
        
        skills_avg = sum(mastery_scores) / len(mastery_scores) if mastery_scores else 0.0
        
        # Weight components
        skills_weight = 0.5
        learning_weight = 0.3
        placement_weight = 0.2
        
        placement_score = placement_performance if placement_performance is not None else 0.0
        
        readiness_score = (
            skills_avg * skills_weight +
            learning_progress * learning_weight +
            placement_score * placement_weight
        )
        
        # Determine status
        if readiness_score >= 80:
            readiness_status = "ready"
        elif readiness_score >= 60:
            readiness_status = "progressing"
        elif readiness_score >= 40:
            readiness_status = "needs_work"
        else:
            readiness_status = "starting"
        
        return {
            "readiness_score": readiness_score,
            "readiness_status": readiness_status,
            "breakdown": {
                "skills": skills_avg,
                "learning": learning_progress,
                "placement": placement_score
            }
        }
