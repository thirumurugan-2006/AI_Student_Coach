from typing import Dict, Any, List
from memory.student_memory import StudentMemory

class KnowledgeGraphManager:
    """
    Manages the knowledge graph for a student.
    Handles graph traversal and concept mastery tracking.
    """
    
    def __init__(self, memory: StudentMemory):
        self.memory = memory

    def get_mastered_concepts(self, student_id: str) -> List[str]:
        """
        Retrieves a list of all concepts the student has mastered.
        """
        profile = self.memory.get_profile(student_id)
        if not profile or "knowledge_graph" not in profile:
            return []
            
        mastered = []
        for topic, concepts in profile["knowledge_graph"].items():
            for concept, status in concepts.items():
                if status == "mastered":
                    mastered.append(concept)
                    
        return mastered

    def get_weak_concepts(self, student_id: str) -> List[str]:
        """
        Retrieves a list of concepts the student struggles with.
        """
        profile = self.memory.get_profile(student_id)
        if not profile or "knowledge_graph" not in profile:
            return []
            
        weak = []
        for topic, concepts in profile["knowledge_graph"].items():
            for concept, status in concepts.items():
                if status == "needs_improvement":
                    weak.append(concept)
                    
        return weak

    def record_concept_status(self, student_id: str, topic: str, concept: str, status: str) -> None:
        """
        Updates the status of a specific concept in the knowledge graph.
        
        Args:
            student_id: The ID of the student.
            topic: The parent topic area (e.g., 'Python').
            concept: The specific concept (e.g., 'Decorators').
            status: The mastery level ('mastered', 'needs_improvement', etc.).
        """
        self.memory.update_concept(student_id, topic, concept, status)
