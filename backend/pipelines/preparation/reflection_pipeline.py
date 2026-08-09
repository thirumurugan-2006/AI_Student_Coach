"""
Reflection Pipeline

Handles student reflection on learning progress and experiences.
Collects qualitative feedback and insights.
"""

from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from skills.reflection.skill import ReflectionSkill
from skills.reflection.schema import ReflectionOutputSchema
from core.logger import logger


class ReflectionPipeline(BasePipeline):
    """
    Pipeline for Reflection skill execution.
    
    Responsible for:
    - Loading learning progress and activities
    - Loading assessment results
    - Generating reflection questions via Groq
    - Validating reflection responses
    - Storing reflection evidence
    - Returning structured results
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize ReflectionPipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
        self.reflection_skill = ReflectionSkill(llm=llm, memory=memory)
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Reflection Pipeline.
        
        Args:
            context: PipelineContext with student information
            
        Returns:
            PipelineResult with reflection question
        """
        logger.info(f"ReflectionPipeline: Starting execution for student {context.student_id}")
        
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
                "learning_progress": context.student_memory.get("learning_progress", 0),
                "completed_topics": context.student_memory.get("completed_topics", []),
                "assessment_performance": context.student_memory.get("assessment_performance", {}),
                "current_activity": context.student_memory.get("current_learning_activity", {}),
                "previous_reflections": context.student_memory.get("reflection_notes", [])
            }
            
            # 6. Execute skill
            logger.info("ReflectionPipeline: Executing ReflectionSkill")
            result = await self.reflection_skill.execute(context=skill_context, schema=ReflectionOutputSchema)
            
            # 7. Validate result
            if not await self.validate_result(result):
                raise ValueError("Reflection skill returned invalid result")
            
            # 8. Extract result data
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
            reflection_result = result_dict.get('result', {})
            
            # 9. Evaluate result
            evaluation = await self.evaluate_result(context, result)
            
            # 10. Create evidence
            evidence = [{
                "type": "reflection_question",
                "question": reflection_result.get('reflection_question', ''),
                "timestamp": context.additional_context.get("timestamp", "")
            }]
            
            # 11. Update student memory
            await self.update_student_memory(context, result)
            
            # 12. Update career intelligence
            await self.update_career_intelligence(context, result)
            
            # 13. Determine next action
            next_action, next_action_reason = await self.determine_next_action(context, result)
            
            # 14. Calculate progress
            progress = 0.7  # Reflection progress
            
            # 15. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result=reflection_result,
                evaluation=evaluation,
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"ReflectionPipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"ReflectionPipeline: Execution failed - {str(e)}")
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="reflection",
                next_action_reason="Reflection question generation failed, retrying",
                error_message=str(e)
            )
    
    async def validate_result(self, result: Any) -> bool:
        """Validate reflection result."""
        logger.debug("ReflectionPipeline: Validating result")
        if result is None:
            return False
        
        # Check if result has expected structure
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return 'result' in result_dict
        
        return True
    
    async def evaluate_result(self, context: PipelineContext, result: Any) -> Dict[str, Any]:
        """Evaluate reflection result."""
        logger.info("ReflectionPipeline: Evaluating result")
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        reflection_result = result_dict.get('result', {})
        
        return {
            "reflection_question": reflection_result.get('reflection_question', ''),
            "reflection_type": reflection_result.get('reflection_type', 'general'),
            "previous_reflections_count": len(context.student_memory.get("reflection_notes", []))
        }
    
    async def update_student_memory(self, context: PipelineContext, result: Any) -> bool:
        """Update student memory with reflection question."""
        logger.info("ReflectionPipeline: Updating student memory")
        if self.memory and context.student_id:
            profile = context.student_memory or self.memory.get_profile(context.student_id)
            if profile:
                result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
                reflection_result = result_dict.get('result', {})
                
                profile["current_reflection_question"] = reflection_result.get('reflection_question', '')
                profile["reflection_in_progress"] = True
                
                context.student_memory = profile
                await self.persist_memory(context)
        return True
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action after reflection."""
        return "readiness", "Reflection captured, evaluating readiness for placement"
