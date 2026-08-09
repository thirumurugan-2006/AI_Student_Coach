"""
Aptitude Pipeline

Handles aptitude test questions for placement simulation.
Generates quantitative, logical reasoning, and verbal questions.
"""

import uuid
from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from skills.placement_aptitude.skill import PlacementAptitudeSkill
from skills.placement_aptitude.schema import AptitudeOutput
from services.question_service import QuestionService
from core.logger import logger


class AptitudePipeline(BasePipeline):
    """
    Pipeline for Aptitude skill execution.
    
    Responsible for:
    - Loading target role and difficulty
    - Loading previous performance
    - Generating aptitude questions via Groq
    - Validating responses
    - Storing questions with backend-generated IDs
    - Checking for duplicates
    - Returning structured results
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize AptitudePipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
        self.question_service = QuestionService()
        self.aptitude_skill = PlacementAptitudeSkill(llm=llm, memory=memory)
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Aptitude Pipeline.
        
        Args:
            context: PipelineContext with student information
            
        Returns:
            PipelineResult with aptitude question
        """
        logger.info(f"AptitudePipeline: Starting execution for student {context.student_id}")
        
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
                "difficulty": context.additional_context.get("difficulty", "medium"),
                "previous_questions": context.question_history,
                "placement_performance": context.student_memory.get("placement_performance", {})
            }
            
            # 7. Execute skill
            logger.info("AptitudePipeline: Executing PlacementAptitudeSkill")
            result = await self.aptitude_skill.execute(context=skill_context, schema=AptitudeOutput)
            
            # 8. Validate result
            if not await self.validate_result(result):
                raise ValueError("Aptitude skill returned invalid result")
            
            # 9. Extract result data
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
            aptitude_result = result_dict.get('result', {})
            
            # 10. Evaluate result
            evaluation = await self.evaluate_result(context, result)
            
            # 11. Create evidence
            evidence = []
            if aptitude_result.get('aptitude_question'):
                evidence.append({
                    "type": "aptitude_question",
                    "question_id": aptitude_result['aptitude_question'].get('question_id'),
                    "question_text": aptitude_result['aptitude_question'].get('question'),
                    "question_type": aptitude_result['aptitude_question'].get('question_type', 'quantitative'),
                    "timestamp": uuid.uuid4().hex
                })
            
            # 12. Update student memory
            await self.update_student_memory(context, result)
            
            # 13. Update career intelligence
            await self.update_career_intelligence(context, result)
            
            # 14. Determine next action
            next_action, next_action_reason = await self.determine_next_action(context, result)
            
            # 15. Calculate progress
            progress = 0.8  # Aptitude progress
            
            # 16. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result=aptitude_result,
                evaluation=evaluation,
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"AptitudePipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"AptitudePipeline: Execution failed - {str(e)}")
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="placement_aptitude",
                next_action_reason="Aptitude question generation failed, retrying",
                error_message=str(e)
            )
    
    async def load_question_history(self, context: PipelineContext) -> PipelineContext:
        """Load previous aptitude questions for uniqueness checking."""
        logger.info("AptitudePipeline: Loading question history")
        try:
            previous_questions = await self.question_service.get_previous_questions(
                student_id=context.student_id,
                skill="placement_aptitude",
                limit=50
            )
            context.question_history = previous_questions
        except Exception as e:
            logger.warning(f"AptitudePipeline: Failed to load question history - {e}")
            context.question_history = []
        return context
    
    async def validate_result(self, result: Any) -> bool:
        """Validate aptitude result."""
        logger.debug("AptitudePipeline: Validating result")
        if result is None:
            return False
        
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return 'result' in result_dict
        
        return True
    
    async def evaluate_result(self, context: PipelineContext, result: Any) -> Dict[str, Any]:
        """Evaluate aptitude result."""
        logger.info("AptitudePipeline: Evaluating result")
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        aptitude_result = result_dict.get('result', {})
        
        return {
            "aptitude_completed": aptitude_result.get('aptitude_completed', False),
            "question_generated": bool(aptitude_result.get('aptitude_question')),
            "question_type": aptitude_result.get('aptitude_question', {}).get('question_type', 'quantitative')
        }
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action based on aptitude completion."""
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        aptitude_result = result_dict.get('result', {})
        aptitude_completed = aptitude_result.get('aptitude_completed', False)
        
        if aptitude_completed:
            return "placement_coding", "Aptitude round completed, moving to coding round"
        else:
            return "placement_aptitude", "Continue aptitude test"
