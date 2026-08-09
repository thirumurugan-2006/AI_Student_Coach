from memory.student_memory import StudentMemory
from core.logger import logger

class StudentService:
    """
    Service layer for student-related operations.
    Bridges the gap between external interfaces (like API routes) and the Student Memory engine.
    """
    
    def __init__(self, memory: StudentMemory):
        self.memory = memory

    def get_or_create_student(self, student_id: str, name: str = "Unknown") -> dict:
        """
        Retrieves a student profile from memory. If it doesn't exist, initializes a new profile.
        """
        profile = self.memory.get_profile(student_id)
        if not profile:
            logger.info(f"Student profile {student_id} not found. Creating a new profile.")
            self.memory.create_student(student_id, name)
            profile = self.memory.get_profile(student_id)
            
        return profile

    def update_career_goal(self, student_id: str, goal: str) -> None:
        """
        Updates the target career goal of the student.
        """
        self.memory.update_goal(student_id, goal)
        logger.info(f"Updated career goal for student {student_id} to '{goal}'.")

    def get_readiness_report(self, student_id: str) -> dict:
        """
        Generates a summary report of the student's current readiness.
        """
        profile = self.memory.get_profile(student_id)
        if not profile:
            raise ValueError("Student not found.")
            
        return {
            "student_id": profile["id"],
            "career_goal": profile.get("career_goal"),
            "readiness_score": profile.get("readiness_score", 0),
            "weak_topics": profile.get("weak_topics", []),
            "strong_topics": profile.get("strong_topics", []),
        }
