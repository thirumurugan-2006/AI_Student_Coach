"""
Technical Pipeline

Handles technical interview questions for placement simulation.
Generates technical questions based on target role, skills, and projects.
"""

import uuid
from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from skills.placement_technical.skill import PlacementTechnicalSkill
from skills.placement_technical.schema import TechnicalOutput
from services.question_service import QuestionService
from core.logger import logger


class TechnicalPipeline(BasePipeline):
    """
    Pipeline for Technical skill execution.
    
    Responsible for:
    - Loading target role and skills
    - Loading projects and skill gaps
    - Loading previous technical questions
    - Generating technical questions via Groq
    - Validating responses
    - Storing questions with backend-generated IDs
    - Checking for duplicates
    - Returning structured results
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize TechnicalPipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
        self.question_service = QuestionService()
        self.technical_skill = PlacementTechnicalSkill(llm=llm, memory=memory)
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Technical Pipeline.
        
        Args:
            context: PipelineContext with student information
            
        Returns:
            PipelineResult with technical question
        """
        logger.info(f"TechnicalPipeline: Starting execution for student {context.student_id}")
        
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
                "target_role": context.target_role or context.student_memory.get("target_role", "Software Engineer"),
                "skills": context.student_memory.get("skills", {}),
                "projects": context.student_memory.get("projects", []),
                "skill_gaps": context.student_memory.get("skill_gaps", []),
                "previous_questions": context.question_history,
                "placement_performance": context.student_memory.get("placement_performance", {})
            }
            
            # 7. Execute skill
            logger.info("TechnicalPipeline: Executing PlacementTechnicalSkill")
            result = await self.technical_skill.execute(context=skill_context, schema=TechnicalOutput)
            
            # 8. Validate result
            if not await self.validate_result(result):
                raise ValueError("Technical skill returned invalid result")
            
            # 9. Extract result data
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
            technical_result = result_dict.get('result', {})
            
            # 10. Evaluate result
            evaluation = await self.evaluate_result(context, result)
            
            # 11. Create evidence
            evidence = []
            if technical_result.get('technical_question'):
                evidence.append({
                    "type": "technical_question",
                    "question_id": technical_result['technical_question'].get('question_id'),
                    "question_text": technical_result['technical_question'].get('question'),
                    "skill": technical_result['technical_question'].get('skill', 'general'),
                    "timestamp": uuid.uuid4().hex
                })
            
            # 12. Update student memory
            await self.update_student_memory(context, result)
            
            # 13. Update career intelligence
            await self.update_career_intelligence(context, result)
            
            # 14. Determine next action
            next_action, next_action_reason = await self.determine_next_action(context, result)
            
            # 15. Calculate progress
            progress = 0.9  # Technical progress
            
            # 16. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result=technical_result,
                evaluation=evaluation,
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"TechnicalPipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"TechnicalPipeline: Execution failed - {str(e)}")
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="placement_technical",
                next_action_reason="Technical question generation failed, retrying",
                error_message=str(e)
            )
    
    async def load_question_history(self, context: PipelineContext) -> PipelineContext:
        """Load previous technical questions for uniqueness checking."""
        logger.info("TechnicalPipeline: Loading question history")
        try:
            previous_questions = await self.question_service.get_previous_questions(
                student_id=context.student_id,
                skill="placement_technical",
                limit=50
            )
            context.question_history = previous_questions
        except Exception as e:
            logger.warning(f"TechnicalPipeline: Failed to load question history - {e}")
            context.question_history = []
        return context
    
    async def validate_result(self, result: Any) -> bool:
        """Validate technical result."""
        logger.debug("TechnicalPipeline: Validating result")
        if result is None:
            return False
        
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return 'result' in result_dict
        
        return True
    
    async def evaluate_result(self, context: PipelineContext, result: Any) -> Dict[str, Any]:
        """Evaluate technical result."""
        logger.info("TechnicalPipeline: Evaluating result")
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        technical_result = result_dict.get('result', {})
        
        return {
            "technical_completed": technical_result.get('technical_completed', False),
            "question_generated": bool(technical_result.get('technical_question')),
            "skill": technical_result.get('technical_question', {}).get('skill', 'general')
        }
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action based on technical completion."""
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        technical_result = result_dict.get('result', {})
        technical_completed = technical_result.get('technical_completed', False)
        
        if technical_completed:
            return "placement_interview", "Technical round completed, moving to interview round"
        else:
            return "placement_technical", "Continue technical interview"
