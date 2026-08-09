"""
Coding Pipeline

Handles coding problems for placement simulation.
Generates DSA and coding questions based on target role and skill level.
"""

import uuid
from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from skills.placement_coding.skill import PlacementCodingSkill
from skills.placement_coding.schema import CodingOutput
from services.question_service import QuestionService
from core.logger import logger


class CodingPipeline(BasePipeline):
    """
    Pipeline for Coding skill execution.
    
    Responsible for:
    - Loading target role and DSA level
    - Loading skill gaps and previous coding history
    - Generating coding problems via Groq
    - Validating responses
    - Storing questions with backend-generated IDs
    - Checking for duplicates
    - Returning structured results
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize CodingPipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
        self.question_service = QuestionService()
        self.coding_skill = PlacementCodingSkill(llm=llm, memory=memory)
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Coding Pipeline.
        
        Args:
            context: PipelineContext with student information
            
        Returns:
            PipelineResult with coding problem
        """
        logger.info(f"CodingPipeline: Starting execution for student {context.student_id}")
        
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
                "dsa_level": context.additional_context.get("dsa_level", "medium"),
                "skill_gaps": context.student_memory.get("skill_gaps", []),
                "previous_questions": context.question_history,
                "placement_performance": context.student_memory.get("placement_performance", {})
            }
            
            # 7. Execute skill
            logger.info("CodingPipeline: Executing PlacementCodingSkill")
            result = await self.coding_skill.execute(context=skill_context, schema=CodingOutput)
            
            # 8. Validate result
            if not await self.validate_result(result):
                raise ValueError("Coding skill returned invalid result")
            
            # 9. Extract result data
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
            coding_result = result_dict.get('result', {})
            
            # 10. Evaluate result
            evaluation = await self.evaluate_result(context, result)
            
            # 11. Create evidence
            evidence = []
            if coding_result.get('coding_question'):
                evidence.append({
                    "type": "coding_question",
                    "question_id": coding_result['coding_question'].get('question_id'),
                    "question_text": coding_result['coding_question'].get('question'),
                    "difficulty": coding_result['coding_question'].get('difficulty', 'medium'),
                    "timestamp": uuid.uuid4().hex
                })
            
            # 12. Update student memory
            await self.update_student_memory(context, result)
            
            # 13. Update career intelligence
            await self.update_career_intelligence(context, result)
            
            # 14. Determine next action
            next_action, next_action_reason = await self.determine_next_action(context, result)
            
            # 15. Calculate progress
            progress = 0.85  # Coding progress
            
            # 16. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result=coding_result,
                evaluation=evaluation,
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"CodingPipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"CodingPipeline: Execution failed - {str(e)}")
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="placement_coding",
                next_action_reason="Coding problem generation failed, retrying",
                error_message=str(e)
            )
    
    async def load_question_history(self, context: PipelineContext) -> PipelineContext:
        """Load previous coding questions for uniqueness checking."""
        logger.info("CodingPipeline: Loading question history")
        try:
            previous_questions = await self.question_service.get_previous_questions(
                student_id=context.student_id,
                skill="placement_coding",
                limit=50
            )
            context.question_history = previous_questions
        except Exception as e:
            logger.warning(f"CodingPipeline: Failed to load question history - {e}")
            context.question_history = []
        return context
    
    async def validate_result(self, result: Any) -> bool:
        """Validate coding result."""
        logger.debug("CodingPipeline: Validating result")
        if result is None:
            return False
        
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return 'result' in result_dict
        
        return True
    
    async def evaluate_result(self, context: PipelineContext, result: Any) -> Dict[str, Any]:
        """Evaluate coding result."""
        logger.info("CodingPipeline: Evaluating result")
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        coding_result = result_dict.get('result', {})
        
        return {
            "coding_completed": coding_result.get('coding_completed', False),
            "question_generated": bool(coding_result.get('coding_question')),
            "difficulty": coding_result.get('coding_question', {}).get('difficulty', 'medium')
        }
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action based on coding completion."""
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        coding_result = result_dict.get('result', {})
        coding_completed = coding_result.get('coding_completed', False)
        
        if coding_completed:
            return "placement_technical", "Coding round completed, moving to technical interview"
        else:
            return "placement_coding", "Continue coding test"
