"""
Career Intelligence Hub Service

Aggregates and manages student intelligence from both Career Preparation
and Placement Simulation modules. Serves as the bridge between modules.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from core.logger import logger


class CareerIntelligenceHub:
    """
    Career Intelligence Hub aggregates student data across modules.
    
    This is NOT an AI agent. It is a student intelligence/state service
    that stores and aggregates data from:
    - Module 1: Career Preparation (Survey, Assessment, Learning, Reflection)
    - Module 2: Placement Simulation (Aptitude, Coding, Technical, Interview, HR)
    """

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def update_profile(
        self,
        student_id: str,
        career_goal: Optional[str] = None,
        target_role: Optional[str] = None,
        target_company: Optional[str] = None,
        experience_level: Optional[str] = None,
        primary_language: Optional[str] = None,
        known_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update student profile information.
        
        Args:
            student_id: The student's ID
            career_goal: Career goal
            target_role: Target role
            target_company: Target company
            experience_level: Experience level
            primary_language: Primary programming language
            known_skills: Known skills list
            
        Returns:
            Updated profile
        """
        profile = {
            "student_id": student_id,
            "career_goal": career_goal,
            "target_role": target_role,
            "target_company": target_company,
            "experience_level": experience_level,
            "primary_language": primary_language,
            "known_skills": known_skills or [],
            "updated_at": datetime.utcnow().isoformat()
        }

        intel = self.get_student_intelligence(student_id)
        intel["profile"].update({k: v for k, v in profile.items() if k != "student_id" and v is not None})
        
        logger.info(f"Updated profile for student {student_id}")
        return profile

    def update_skills(
        self,
        student_id: str,
        skill: str,
        mastery_level: str,
        score: float,
        evidence_type: str
    ) -> Dict[str, Any]:
        """
        Update skill mastery information.
        
        Args:
            student_id: The student's ID
            skill: The skill name
            mastery_level: needs_improvement, learning, or mastered
            score: The score for this skill
            evidence_type: Type of evidence (assessment, placement, etc.)
            
        Returns:
            Updated skill information
        """
        skill_data = {
            "student_id": student_id,
            "skill": skill,
            "mastery_level": mastery_level,
            "score": score,
            "evidence_type": evidence_type,
            "updated_at": datetime.utcnow().isoformat()
        }

        intel = self.get_student_intelligence(student_id)
        intel["skills"][skill] = score
        
        logger.info(f"Updated skill {skill} for student {student_id}: {mastery_level}")
        return skill_data

    def update_skill_gaps(
        self,
        student_id: str,
        skill_gaps: List[str],
        source: str
    ) -> Dict[str, Any]:
        """
        Update skill gaps information.
        
        Args:
            student_id: The student's ID
            skill_gaps: List of skill gaps
            source: Source of gap identification (assessment, placement, etc.)
            
        Returns:
            Updated skill gaps
        """
        gaps_data = {
            "student_id": student_id,
            "skill_gaps": skill_gaps,
            "source": source,
            "updated_at": datetime.utcnow().isoformat()
        }

        intel = self.get_student_intelligence(student_id)
        intel["skill_gaps"] = skill_gaps
        
        logger.info(f"Updated skill gaps for student {student_id} from {source}")
        return gaps_data

    def add_evidence(
        self,
        student_id: str,
        evidence_type: str,
        skill: str,
        score: float,
        is_correct: Optional[bool] = None,
        strengths: Optional[List[str]] = None,
        weaknesses: Optional[List[str]] = None,
        feedback: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add evidence from assessments or placement activities.
        
        Args:
            student_id: The student's ID
            evidence_type: Type of evidence (survey, assessment, placement_aptitude, etc.)
            skill: The skill being assessed
            score: The score achieved
            is_correct: Whether the answer was correct (for MCQ)
            strengths: List of strengths identified
            weaknesses: List of weaknesses identified
            feedback: Feedback provided
            metadata: Additional metadata
            
        Returns:
            Evidence record
        """
        evidence = {
            "student_id": student_id,
            "evidence_type": evidence_type,
            "skill": skill,
            "score": score,
            "is_correct": is_correct,
            "strengths": strengths or [],
            "weaknesses": weaknesses or [],
            "feedback": feedback,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }

        intel = self.get_student_intelligence(student_id)
        intel["evidence"].append(evidence)
        
        logger.info(f"Added evidence for student {student_id}: {evidence_type} - {skill}")
        return evidence

    def update_learning_progress(
        self,
        student_id: str,
        topic: str,
        progress: float,
        completed: bool = False
    ) -> Dict[str, Any]:
        """
        Update learning progress.
        
        Args:
            student_id: The student's ID
            topic: The learning topic
            progress: Progress percentage (0-100)
            completed: Whether the topic is completed
            
        Returns:
            Updated learning progress
        """
        learning_data = {
            "student_id": student_id,
            "topic": topic,
            "progress": progress,
            "completed": completed,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Updated learning progress for student {student_id}: {topic} - {progress}%")
        return learning_data

    def update_placement_performance(
        self,
        student_id: str,
        placement_type: str,
        score: float,
        round_number: int,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update placement simulation performance.
        
        Args:
            student_id: The student's ID
            placement_type: Type of placement test (aptitude, coding, technical, interview, hr)
            score: The score achieved
            round_number: The round number
            details: Additional details
            
        Returns:
            Updated placement performance
        """
        placement_data = {
            "student_id": student_id,
            "placement_type": placement_type,
            "score": score,
            "round_number": round_number,
            "details": details or {},
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Updated placement performance for student {student_id}: {placement_type} - {score}")
        return placement_data

    def update_readiness(
        self,
        student_id: str,
        readiness_score: float,
        readiness_status: str,
        breakdown: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Update overall readiness score.
        
        Args:
            student_id: The student's ID
            readiness_score: Overall readiness score (0-100)
            readiness_status: Status (ready, progressing, needs_work, starting)
            breakdown: Breakdown by component
            
        Returns:
            Updated readiness information
        """
        readiness_data = {
            "student_id": student_id,
            "readiness_score": readiness_score,
            "readiness_status": readiness_status,
            "breakdown": breakdown or {},
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Updated readiness for student {student_id}: {readiness_status} ({readiness_score})")
        return readiness_data

    def update_recommendations(
        self,
        student_id: str,
        recommendations: List[str],
        priority_action: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update recommendations.
        
        Args:
            student_id: The student's ID
            recommendations: List of recommendations
            priority_action: The single most important action
            
        Returns:
            Updated recommendations
        """
        recommendations_data = {
            "student_id": student_id,
            "recommendations": recommendations,
            "priority_action": priority_action,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Updated recommendations for student {student_id}")
        return recommendations_data

    def get_student_intelligence(
        self,
        student_id: str
    ) -> Dict[str, Any]:
        """
        Get complete student intelligence from all modules.
        
        Args:
            student_id: The student's ID
            
        Returns:
            Complete student intelligence profile
        """
        # This would typically query the database for all student data
        # For now, return stored intelligence or initialize a new profile
        
        if student_id in self._store:
            return self._store[student_id]

        intelligence = {
            "student_id": student_id,
            "profile": {},
            "skills": {},
            "skill_gaps": [],
            "evidence": [],
            "learning_progress": {},
            "placement_performance": {},
            "readiness": {},
            "recommendations": [],
            "last_updated": datetime.utcnow().isoformat()
        }
        self._store[student_id] = intelligence
        
        logger.info(f"Retrieved intelligence for student {student_id}")
        return intelligence

    def update_intelligence(self, student_id: str, result: Any) -> Dict[str, Any]:
        """Merge pipeline result data into student intelligence."""
        intel = self.get_student_intelligence(student_id)

        if isinstance(result, dict):
            for key in ("profile", "skills", "skill_gaps", "learning_progress",
                        "placement_performance", "readiness", "recommendations"):
                if key not in result:
                    continue
                value = result[key]
                if isinstance(intel.get(key), dict) and isinstance(value, dict):
                    intel[key].update(value)
                elif isinstance(intel.get(key), list) and isinstance(value, list):
                    intel[key].extend(value)
                else:
                    intel[key] = value

            if "evidence" in result and isinstance(result["evidence"], list):
                for ev in result["evidence"]:
                    if isinstance(ev, dict):
                        self.add_evidence(
                            student_id,
                            evidence_type=ev.get("type", ev.get("evidence_type", "pipeline")),
                            skill=ev.get("skill", "general"),
                            score=float(ev.get("score", 1.0)),
                            is_correct=ev.get("is_correct"),
                            metadata=ev,
                        )

        intel["last_updated"] = datetime.utcnow().isoformat()
        logger.info(f"Updated intelligence for student {student_id}")
        return intel

    def calculate_next_best_action(
        self,
        student_id: str,
        current_stage: str,
        readiness_status: str,
        skill_gaps: List[str],
        learning_progress: float
    ) -> str:
        """
        Calculate the next best action based on current state.
        
        This is NOT an LLM decision - it's a rule-based determination
        based on the student's current state and readiness.
        
        Args:
            student_id: The student's ID
            current_stage: Current workflow stage
            readiness_status: Current readiness status
            skill_gaps: List of skill gaps
            learning_progress: Learning progress percentage
            
        Returns:
            Next action (survey, assessment, learning, placement, dashboard)
        """
        # Rule-based next action determination
        if current_stage == "survey":
            return "assessment"
        elif current_stage == "assessment":
            if skill_gaps:
                return "learning"
            else:
                return "learning"  # Even without gaps, continue learning
        elif current_stage == "learning":
            if readiness_status == "ready":
                return "placement"
            else:
                return "learning"  # Continue learning
        elif current_stage == "placement":
            return "dashboard"  # After placement, show dashboard
        else:
            return "dashboard"
