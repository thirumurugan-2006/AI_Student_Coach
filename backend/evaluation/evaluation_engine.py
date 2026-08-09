from typing import Any, Dict
from memory.student_memory import StudentMemory
from evaluation.confidence import ConfidenceCalculator
from evaluation.progress import ProgressCalculator
from evaluation.readiness import ReadinessCalculator
from core.logger import logger

class EvaluationEngine:
    """
    Centralized evaluation processor.
    No skill is allowed to calculate scores internally; they must route 
    their raw results here for consistent evaluation across the system.
    
    Updates:
    - Knowledge Graph
    - Readiness Score
    - Confidence
    - Progress
    - Student Memory
    """
    
    def __init__(self, memory: StudentMemory):
        self.memory = memory
        self.confidence_calculator = ConfidenceCalculator()
        self.progress_calculator = ProgressCalculator()
        self.readiness_calculator = ReadinessCalculator()

    def process(self, student_id: str, skill_name: str, result: Dict[str, Any]) -> None:
        """
        Process the result from a specific skill and update the memory accordingly.
        
        Args:
            student_id: The ID of the student.
            skill_name: The name of the skill that produced the result.
            result: The structured output from the skill execution.
        """
        logger.info(f"Evaluation Engine: Processing {skill_name} for student {student_id}")
        
        if skill_name == "assessment":
            self._process_assessment(student_id, result)
        elif skill_name == "survey":
            self._process_survey(student_id, result)
        elif skill_name == "interview":
            self._process_interview(student_id, result)
        elif skill_name == "reflection":
            self._process_reflection(student_id, result)
        elif skill_name == "learning":
            self._process_learning(student_id, result)
        elif skill_name.startswith("placement."):
            self._process_placement(student_id, result)
        
        # After processing any skill, recalculate all metrics
        self._recalculate_metrics(student_id)

    def _process_assessment(self, student_id: str, result: Dict[str, Any]) -> None:
        """Handles the assessment skill result routing."""
        self.memory.add_assessment(student_id, result)
        
        # Update knowledge graph based on assessment performance
        for topic, evaluation in result.get("topic_evaluations", {}).items():
            for concept, status in evaluation.items():
                self.memory.update_concept(student_id, topic, concept, status)
                
                # Track weak and strong topics
                if status == "weak":
                    self.memory.add_weak_topic(student_id, topic)
                elif status == "strong":
                    self.memory.add_strong_topic(student_id, topic)

    def _process_survey(self, student_id: str, result: Dict[str, Any]) -> None:
        """Handles the survey skill result routing."""
        if "career_goal" in result:
            self.memory.update_goal(student_id, result["career_goal"])
        
        # Update profile from survey data
        if hasattr(result, "profile"):
            self.memory.update_from_survey(student_id, result.profile)

    def _process_interview(self, student_id: str, result: Dict[str, Any]) -> None:
        """Handles the interview skill result routing."""
        self.memory.add_interview(student_id, result)
        
        if "feedback" in result:
            self.memory.add_feedback(student_id, result["feedback"])
        
        # Update confidence based on interview performance
        if "overall_score" in result:
            profile = self.memory.get_profile(student_id)
            if profile:
                current_confidence = profile.get("confidence", 50)
                new_confidence = self.confidence_calculator.update_from_interview(
                    current_confidence, result["overall_score"]
                )
                profile["confidence"] = new_confidence

    def _process_reflection(self, student_id: str, result: Dict[str, Any]) -> None:
        """Handles the reflection skill result routing."""
        self.memory.add_reflection(student_id, result)
        
        # Update confidence from reflection
        if "confidence_score" in result:
            profile = self.memory.get_profile(student_id)
            if profile:
                profile["confidence"] = result["confidence_score"]

    def _process_learning(self, student_id: str, result: Dict[str, Any]) -> None:
        """Handles the learning skill result routing."""
        if "roadmap" in result:
            self.memory.update_roadmap(student_id, result["roadmap"])

        if "completed_topics" in result:
            profile = self.memory.get_profile(student_id)
            if profile:
                profile["completed_topics"] = result["completed_topics"]

    def _process_placement(self, student_id: str, result: Dict[str, Any]) -> None:
        """Handles the placement skill result routing."""
        evaluation = result.get("evaluation", result)
        score = evaluation.get("score", 0.0)
        topics = evaluation.get("topics", [])

        # Update skills based on placement performance
        for topic in topics:
            current_score = self.memory.students.get(student_id, {}).get("skills", {}).get(topic, 50)
            new_score = min(100, max(0, current_score + (score - 50) * 0.1))
            self.memory.update_skill(student_id, topic, round(new_score, 2))

    def _recalculate_metrics(self, student_id: str) -> None:
        """
        Recalculate all metrics after a skill execution.
        """
        profile = self.memory.get_profile(student_id)
        if not profile:
            return
        
        # Calculate readiness score
        readiness = self.readiness_calculator.calculate(profile)
        profile["readiness_score"] = readiness
        
        # Calculate progress
        progress = self.progress_calculator.calculate(profile)
        profile["progress"] = progress
        
        logger.info(f"Metrics recalculated for student {student_id}: readiness={readiness}, progress={progress}")
