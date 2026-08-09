from typing import List, Dict
from memory.student_memory import StudentMemory

class ConfidenceCalculator:
    """
    Calculates and tracks student confidence levels.
    """

    def __init__(self, memory: StudentMemory = None):
        self.memory = memory

    def update_from_interview(self, current_confidence: float, interview_score: float) -> float:
        """
        Update confidence based on interview performance.
        
        Args:
            current_confidence: Current confidence score (0-100).
            interview_score: Interview performance score (0-100).
            
        Returns:
            Updated confidence score.
        """
        # Weighted average: 70% current confidence, 30% interview performance
        new_confidence = (current_confidence * 0.7) + (interview_score * 0.3)
        return min(100, max(0, new_confidence))

    def calculate_from_reflections(self, reflection_notes: List[Dict]) -> float:
        """
        Calculate confidence from reflection history.
        
        Args:
            reflection_notes: List of reflection entries.
            
        Returns:
            Confidence score (0-100).
        """
        if not reflection_notes:
            return 50.0  # Default confidence
        
        confidence_scores = []
        for note in reflection_notes:
            if "confidence_score" in note:
                confidence_scores.append(note["confidence_score"])
            elif "confidence_level" in note:
                # Convert string level to numeric
                level_map = {"low": 25, "medium": 50, "high": 75, "very_high": 90}
                confidence_scores.append(level_map.get(note["confidence_level"], 50))
        
        if not confidence_scores:
            return 50.0
        
        return sum(confidence_scores) / len(confidence_scores)
