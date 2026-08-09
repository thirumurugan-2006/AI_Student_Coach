"""
Placement Simulator

Specialized orchestrator for placement preparation workflow.
Controls the placement assessment and recommendation flow.
"""

from typing import Dict, Any
from pydantic import BaseModel
from memory.student_memory import StudentMemory
from core.llm_interface import LLMInterface
from skills.placement.skill import PlacementSkill
from skills.placement.schema import PlacementOutput
from core.logger import logger


class PlacementSimulator:
    """
    Placement preparation orchestrator.
    
    Responsibilities:
    - Assess student placement readiness
    - Provide actionable recommendations
    - Track placement progress
    - Generate placement reports
    
    Workflow is controlled by this orchestrator, not the LLM.
    The LLM only provides assessment and recommendations.
    """
    
    def __init__(self, memory: StudentMemory, llm: LLMInterface):
        self.memory = memory
        self.llm = llm
        self.placement_skill = PlacementSkill(llm=llm, memory=memory)
    
    async def assess_placement_readiness(
        self,
        student_id: str,
        target_role: str = None,
        target_companies: list = None
    ) -> PlacementOutput:
        """
        Assess student's placement readiness.
        
        Args:
            student_id: Student's user ID
            target_role: Optional target job role
            target_companies: Optional list of target companies
            
        Returns:
            PlacementOutput with assessment and recommendations
        """
        logger.info(f"Placement Simulator: Assessing readiness for student {student_id}")
        
        # Ensure student exists
        profile = self.memory.get_profile(student_id)
        if not profile:
            logger.warning(f"Student {student_id} not found. Creating default profile.")
            self.memory.create_student(student_id, "Unknown Student")
        
        # Build context for placement skill
        context = {
            "student_id": student_id,
            "target_role": target_role or profile.get("career_goal", "Software Engineer"),
            "target_companies": target_companies or profile.get("target_company", [])
        }
        
        # Execute placement skill
        result = await self.placement_skill.execute(context=context, schema=PlacementOutput)
        
        # Save assessment to memory
        from database.session import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            await self.memory.save(db, student_id)
        
        logger.info(f"Placement Simulator: Assessment complete for student {student_id}")
        return result
    
    async def get_placement_progress(self, student_id: str) -> Dict[str, Any]:
        """
        Get student's placement progress summary.
        
        Args:
            student_id: Student's user ID
            
        Returns:
            Dictionary with placement progress information
        """
        profile = self.memory.get_profile(student_id)
        if not profile:
            return {"error": "Student not found"}
        
        return {
            "student_id": student_id,
            "career_goal": profile.get("career_goal"),
            "target_company": profile.get("target_company"),
            "readiness_score": profile.get("readiness_score", 0),
            "completed_topics": profile.get("completed_topics", []),
            "roadmap": profile.get("roadmap", [])
        }
