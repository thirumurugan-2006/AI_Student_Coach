"""
HR Pipeline

Handles HR interview questions for placement simulation.
Generates HR questions based on student profile, career goal, and experience.
"""

import uuid
from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from skills.placement_hr.skill import PlacementHRSkill
from skills.placement_hr.schema import HROutput
from services.question_service import QuestionService
from core.logger import logger


class HRPipeline(BasePipeline):
    """
    Pipeline for HR skill execution.
    
    Responsible for:
    - Loading student profile and career goal
    - Loading projects and experience
    - Loading previous HR questions
    - Generating HR questions via Groq
    - Validating responses
    - Storing questions with backend-generated IDs
    - Checking for duplicates
    - Returning structured results
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize HRPipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
        self.question_service = QuestionService()
        self.hr_skill = PlacementHRSkill(llm=llm, memory=memory)
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the HR Pipeline.
        
        Args:
            context: PipelineContext with student information
            
        Returns:
            PipelineResult with HR question
        """
        logger.info(f"HRPipeline: Starting execution for student {context.student_id}")
        
        try:
            # 1. Load workflow state
            context = await self.load_workflow_state(context)
            
            # 2. Load student context
            context = await self.load_student_context(context)
            
            # 3. Load career intelligence
            context = await self.load_career_intelligence(context)
            
            # 4. Load previous activity
            context = await self.load_previous_activity(context)
            
            # 5. Load question history for uniqueness
            context = await self.load_question_history(context)
            
            # 6. Build execution context for skill
            skill_context = {
                "student_id": context.student_id,
                "student_profile": context.student_memory,
                "career_goal": context.student_memory.get("career_goal", ""),
                "projects": context.student_memory.get("projects", []),
                "experience": context.student_memory.get("experience", ""),
                "previous_questions": context.question_history,
                "placement_performance": context.student_memory.get("placement_performance", {})
            }
            
            # 7. Execute skill
            logger.info("HRPipeline: Executing PlacementHRSkill")
            result = await self.hr_skill.execute(context=skill_context, schema=HROutput)
            
            # 8. Validate result
            if not await self.validate_result(result):
                raise ValueError("HR skill returned invalid result")
            
            # 9. Extract result data
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
            hr_result = result_dict.get('result', {})
            
            # 10. Evaluate result
            evaluation = await self.evaluate_result(context, result)
            
            # 11. Create evidence
            evidence = []
            if hr_result.get('hr_question'):
                evidence.append({
                    "type": "hr_question",
                    "question_id": hr_result['hr_question'].get('question_id'),
                    "question_text": hr_result['hr_question'].get('question'),
                    "question_category": hr_result['hr_question'].get('question_category', 'general'),
                    "timestamp": uuid.uuid4().hex
                })
            
            # 12. Update student memory
            await self.update_student_memory(context, result)
            
            # 13. Update career intelligence
            await self.update_career_intelligence(context, result)
            
            # 14. Determine next action
            next_action, next_action_reason = await self.determine_next_action(context, result)
            
            # 15. Calculate progress
            progress = 0.98  # HR progress
            
            # 16. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result=hr_result,
                evaluation=evaluation,
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"HRPipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"HRPipeline: Execution failed - {str(e)}")
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="placement_hr",
                next_action_reason="HR question generation failed, retrying",
                error_message=str(e)
            )
    
    async def load_question_history(self, context: PipelineContext) -> PipelineContext:
        """Load previous HR questions for uniqueness checking."""
        logger.info("HRPipeline: Loading question history")
        try:
            previous_questions = await self.question_service.get_previous_questions(
                student_id=context.student_id,
                skill="placement_hr",
                limit=50
            )
            context.question_history = previous_questions
        except Exception as e:
            logger.warning(f"HRPipeline: Failed to load question history - {e}")
            context.question_history = []
        return context
    
    async def validate_result(self, result: Any) -> bool:
        """Validate HR result."""
        logger.debug("HRPipeline: Validating result")
        if result is None:
            return False
        
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return 'result' in result_dict
        
        return True
    
    async def evaluate_result(self, context: PipelineContext, result: Any) -> Dict[str, Any]:
        """Evaluate HR result."""
        logger.info("HRPipeline: Evaluating result")
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        hr_result = result_dict.get('result', {})
        
        return {
            "hr_completed": hr_result.get('hr_completed', False),
            "question_generated": bool(hr_result.get('hr_question')),
            "question_category": hr_result.get('hr_question', {}).get('question_category', 'general')
        }
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action based on HR completion."""
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        hr_result = result_dict.get('result', {})
        hr_completed = hr_result.get('hr_completed', False)
        
        if hr_completed:
            return "placement_report", "HR round completed, generating placement report"
        else:
            return "placement_hr", "Continue HR interview"
