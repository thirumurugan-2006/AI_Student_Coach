from typing import Dict, Any

class ReadinessCalculator:
    """
    Dedicated logic for deeper readiness analysis beyond just an average score.
    Separates the mathematical evaluation logic from the memory storage.
    """

    def __init__(self, memory = None):
        self.memory = memory

    def calculate(self, profile: Dict[str, Any]) -> float:
        """
        Calculate overall readiness score from student profile.
        
        Args:
            profile: Student profile dictionary.
            
        Returns:
            Readiness score (0-100).
        """
        # Technical skills component (40%)
        skills = profile.get("skills", {})
        technical_score = 0
        if skills:
            technical_score = sum(skills.values()) / len(skills)
        
        # Interview performance component (30%)
        interview_history = profile.get("interview_history", [])
        interview_score = 0
        if interview_history:
            total_interview_score = sum(i.get("overall_score", 0) for i in interview_history)
            interview_score = total_interview_score / len(interview_history)
        
        # Confidence component (20%)
        confidence = profile.get("confidence", 50)
        
        # Roadmap completion component (10%)
        roadmap = profile.get("roadmap", [])
        completed = profile.get("completed_topics", [])
        roadmap_completion = 0
        if roadmap:
            completed_items = sum(1 for item in roadmap if item in completed)
            roadmap_completion = (completed_items / len(roadmap)) * 100
        
        # Weighted combination
        combined_score = (
            technical_score * 0.4 +
            interview_score * 0.3 +
            confidence * 0.2 +
            roadmap_completion * 0.1
        )
        
        return min(100, max(0, round(combined_score, 2)))

    def calculate_industry_readiness(self, student_id: str) -> dict:
        """
        Calculates a multi-dimensional readiness metric based on skills,
        interview history, and knowledge graph completion.
        """
        profile = self.memory.get_profile(student_id) if self.memory else None
        if not profile:
            return {"status": "unknown", "score": 0}
        
        score = self.calculate(profile)
        
        return {
            "status": "ready" if score > 75 else "needs_preparation",
            "score": score,
            "technical_component": profile.get("readiness_score", 0),
            "interview_component": score * 0.3
        }
