from typing import Dict, Any

class ProgressCalculator:
    """
    Calculates completion rates and manages roadmap advancement.
    """

    def __init__(self, memory = None):
        self.memory = memory

    def calculate(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall progress metrics from student profile.
        
        Args:
            profile: Student profile dictionary.
            
        Returns:
            Progress metrics dictionary.
        """
        roadmap = profile.get("roadmap", [])
        completed = profile.get("completed_topics", [])
        
        # Calculate roadmap completion
        total_items = len(roadmap)
        completed_items = sum(1 for item in roadmap if item in completed)
        roadmap_percentage = (completed_items / total_items * 100) if total_items > 0 else 0
        
        # Calculate assessment progress
        assessment_count = len(profile.get("assessment_history", []))
        
        # Calculate interview progress
        interview_count = len(profile.get("interview_history", []))
        
        # Calculate reflection progress
        reflection_count = len(profile.get("reflection_notes", []))
        
        return {
            "roadmap_completion": round(roadmap_percentage, 2),
            "assessments_completed": assessment_count,
            "interviews_completed": interview_count,
            "reflections_completed": reflection_count,
            "total_progress": round((roadmap_percentage * 0.5 + min(assessment_count * 10, 50) * 0.3 + min(interview_count * 10, 50) * 0.2), 2)
        }
