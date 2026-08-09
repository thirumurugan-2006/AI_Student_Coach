"""
Learning Pipeline

Generates and manages personalized learning activities based on roadmap.
Controls the learning phase of career preparation.
"""

from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from skills.learning.skill import LearningSkill
from skills.learning.schema import LearningOutputSchema
from core.logger import logger


def _roadmap_topic_count(student_memory: dict) -> int:
    roadmap = student_memory.get("roadmap", [])
    if isinstance(roadmap, dict):
        return len(roadmap.get("topics", []))
    if isinstance(roadmap, list):
        return len(roadmap)
    return 0


class LearningPipeline(BasePipeline):
    """
    Pipeline for Learning skill execution.
    
    Responsible for:
    - Loading roadmap and skill gaps
    - Loading assessment results
    - Loading student progress
    - Generating learning activity via Groq
    - Validating learning content
    - Storing learning activity
    - Returning structured results
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize LearningPipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
        self.learning_skill = LearningSkill(llm=llm, memory=memory)
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Learning Pipeline.
        
        Args:
            context: PipelineContext with student information
            
        Returns:
            PipelineResult with learning activity
        """
        logger.info(f"LearningPipeline: Starting execution for student {context.student_id}")
        
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
                "roadmap": context.student_memory.get("roadmap", {}),
                "skill_gaps": context.student_memory.get("skill_gaps", []),
                "completed_topics": context.student_memory.get("completed_topics", []),
                "assessment_performance": context.student_memory.get("assessment_performance", {}),
                "requested_topic": context.additional_context.get("requested_topic", "")
            }
            
            # 6. Execute skill
            logger.info("LearningPipeline: Executing LearningSkill")
            result = await self.learning_skill.execute(context=skill_context, schema=LearningOutputSchema)
            
            # 7. Validate result
            if not await self.validate_result(result):
                raise ValueError("Learning skill returned invalid result")
            
            # 8. Extract result data
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
            learning_result = result_dict.get('result', {})
            
            # 9. Evaluate result
            evaluation = await self.evaluate_result(context, result)
            
            # 10. Create evidence
            evidence = [{
                "type": "learning_activity",
                "topic": learning_result.get('topic', ''),
                "activity_type": learning_result.get('activity_type', ''),
                "timestamp": context.additional_context.get("timestamp", "")
            }]
            
            # 11. Update student memory
            await self.update_student_memory(context, result)
            
            # 12. Update career intelligence
            await self.update_career_intelligence(context, result)
            
            # 13. Determine next action
            next_action, next_action_reason = await self.determine_next_action(context, result)
            
            # 14. Calculate progress
            completed_count = len(context.student_memory.get("completed_topics", []))
            total_topics = _roadmap_topic_count(context.student_memory)
            progress = 0.4 + (completed_count / total_topics * 0.2) if total_topics > 0 else 0.4
            
            # 15. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result=learning_result,
                evaluation=evaluation,
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"LearningPipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"LearningPipeline: Execution failed - {str(e)}")
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="learning",
                next_action_reason="Learning activity generation failed, retrying",
                error_message=str(e)
            )
    
    async def validate_result(self, result: Any) -> bool:
        """Validate learning result."""
        logger.debug("LearningPipeline: Validating result")
        if result is None:
            return False
        
        # Check if result has expected structure
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return 'result' in result_dict
        
        return True
    
    async def evaluate_result(self, context: PipelineContext, result: Any) -> Dict[str, Any]:
        """Evaluate learning result."""
        logger.info("LearningPipeline: Evaluating result")
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        learning_result = result_dict.get('result', {})
        
        completed_count = len(context.student_memory.get("completed_topics", []))
        total_topics = _roadmap_topic_count(context.student_memory)
        
        return {
            "topic": learning_result.get('topic', ''),
            "activity_type": learning_result.get('activity_type', ''),
            "completed_topics": completed_count,
            "total_topics": total_topics,
            "learning_progress": round(completed_count / total_topics * 100, 2) if total_topics > 0 else 0.0
        }
    
    async def update_student_memory(self, context: PipelineContext, result: Any) -> bool:
        """Update student memory with learning activity."""
        logger.info("LearningPipeline: Updating student memory")
        if self.memory and context.student_id:
            profile = context.student_memory or self.memory.get_profile(context.student_id)
            if profile:
                result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
                learning_result = result_dict.get('result', {})
                
                profile["current_learning_activity"] = learning_result
                profile["learning_in_progress"] = True
                
                context.student_memory = profile
                await self.persist_memory(context)
        return True
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action based on learning progress."""
        completed_count = len(context.student_memory.get("completed_topics", []))
        total_topics = _roadmap_topic_count(context.student_memory)
        
        # If learning is substantially complete, move to reflection
        if total_topics > 0 and completed_count / total_topics >= 0.7:
            return "reflection", "Learning substantially complete, requesting reflection"
        else:
            return "learning", "Continue learning to build skills"
