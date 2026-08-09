"""
Roadmap Pipeline

Generates personalized learning roadmap based on skill gaps and career goals.
Uses Groq to create structured learning path.
"""

from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from skills.roadmap.skill import RoadmapSkill
from skills.roadmap.schema import RoadmapOutput
from core.logger import logger


class RoadmapPipeline(BasePipeline):
    """
    Pipeline for Roadmap generation.
    
    Responsible for:
    - Loading career goal and target role
    - Loading skills and skill gaps
    - Loading assessment results
    - Loading learning history
    - Generating roadmap via Groq
    - Validating roadmap structure
    - Storing roadmap in memory
    - Returning structured results
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize RoadmapPipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
        self.roadmap_skill = RoadmapSkill(llm=llm, memory=memory)
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Roadmap Pipeline.
        
        Args:
            context: PipelineContext with student information
            
        Returns:
            PipelineResult with learning roadmap
        """
        logger.info(f"RoadmapPipeline: Starting execution for student {context.student_id}")
        
        try:
            # 1. Load workflow state
            context = await self.load_workflow_state(context)
            
            # 2. Load student context
            context = await self.load_student_context(context)
            
            # 3. Load career intelligence
            context = await self.load_career_intelligence(context)
            
            # 4. Load previous activity
            context = await self.load_previous_activity(context)
            
            # 5. Build execution context for skill
            skill_context = {
                "student_id": context.student_id,
                "career_goal": context.student_memory.get("career_goal", ""),
                "target_role": context.target_role or context.student_memory.get("target_role", "Software Engineer"),
                "skills": context.student_memory.get("skills", {}),
                "skill_gaps": context.student_memory.get("skill_gaps", []),
                "assessment_performance": context.student_memory.get("assessment_performance", {}),
                "learning_history": context.student_memory.get("learning_history", [])
            }
            
            # 6. Execute skill
            logger.info("RoadmapPipeline: Executing RoadmapSkill")
            result = await self.roadmap_skill.execute(context=skill_context, schema=RoadmapOutput)
            
            # 7. Validate result
            if not await self.validate_result(result):
                raise ValueError("Roadmap skill returned invalid result")
            
            # 8. Extract result data
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
            roadmap_result = result_dict.get('result', {})
            
            # 9. Evaluate result
            evaluation = await self.evaluate_result(context, result)
            
            # 10. Create evidence
            evidence = [{
                "type": "roadmap_generation",
                "career_goal": roadmap_result.get('career_goal', ''),
                "target_role": roadmap_result.get('target_role', ''),
                "milestones_count": len(roadmap_result.get('milestones', [])),
                "topics_count": len(roadmap_result.get('topics', [])),
                "timestamp": context.additional_context.get("timestamp", "")
            }]
            
            # 11. Update student memory
            await self.update_student_memory(context, result)
            
            # 12. Update career intelligence
            await self.update_career_intelligence(context, result)
            
            # 13. Determine next action
            next_action, next_action_reason = await self.determine_next_action(context, result)
            
            # 14. Calculate progress
            progress = 0.4  # Roadmap progress
            
            # 15. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result=roadmap_result,
                evaluation=evaluation,
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"RoadmapPipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"RoadmapPipeline: Execution failed - {str(e)}")
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="roadmap",
                next_action_reason="Roadmap generation failed, retrying",
                error_message=str(e)
            )
    
    async def validate_result(self, result: Any) -> bool:
        """Validate roadmap result."""
        logger.debug("RoadmapPipeline: Validating result")
        if result is None:
            return False
        
        # Check if result has expected structure
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return 'result' in result_dict
        
        return True
    
    async def evaluate_result(self, context: PipelineContext, result: Any) -> Dict[str, Any]:
        """Evaluate roadmap result."""
        logger.info("RoadmapPipeline: Evaluating result")
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        roadmap_result = result_dict.get('result', {})
        
        return {
            "career_goal": roadmap_result.get('career_goal', ''),
            "target_role": roadmap_result.get('target_role', ''),
            "milestones_count": len(roadmap_result.get('milestones', [])),
            "topics_count": len(roadmap_result.get('topics', [])),
            "estimated_duration": roadmap_result.get('estimated_duration', '')
        }
    
    async def update_student_memory(self, context: PipelineContext, result: Any) -> bool:
        """Update student memory with roadmap."""
        logger.info("RoadmapPipeline: Updating student memory")
        if self.memory and context.student_id:
            profile = context.student_memory or self.memory.get_profile(context.student_id)
            if profile:
                result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
                roadmap_result = result_dict.get('result', {})
                
                profile["roadmap"] = roadmap_result
                profile["roadmap_completed"] = True
                profile["completed_topics"] = []
                
                context.student_memory = profile
                await self.persist_memory(context)
        return True
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action after roadmap generation."""
        return "learning", "Roadmap generated, starting learning phase"
