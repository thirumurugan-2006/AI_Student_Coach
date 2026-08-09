"""
Assessment Pipeline

Controls the execution of the Assessment skill for skill evaluation.
Follows the standard Pipeline lifecycle.
"""

import uuid
from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from skills.assessment.skill import AssessmentSkill
from skills.assessment.schema import AssessmentOutputSchema
from services.question_service import QuestionService
from core.logger import logger


class AssessmentPipeline(BasePipeline):
    """
    Pipeline for Assessment skill execution.
    
    Responsible for:
    - Loading student context and assessment instructions
    - Generating assessment questions via Groq
    - Validating responses
    - Storing questions with backend-generated IDs
    - Checking for duplicates
    - Returning structured results
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize AssessmentPipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
        self.question_service = QuestionService()
        self.assessment_skill = AssessmentSkill(llm=llm, memory=memory)
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Assessment Pipeline.
        
        Args:
            context: PipelineContext with student information
            
        Returns:
            PipelineResult with assessment question
        """
        logger.info(f"AssessmentPipeline: Starting execution for student {context.student_id}")
        
        try:
            # 1. Load workflow state
            context = await self.load_workflow_state(context)
            
            # 2. Load student context
            context = await self.load_student_context(context)
            
            # 3. Load career intelligence
            context = await self.load_career_intelligence(context)
            
            # 4. Load skill instructions
            instructions = await self.load_skill_instructions(context)
            
            # 5. Load previous activity
            context = await self.load_previous_activity(context)
            
            # 6. Load question history for uniqueness
            context = await self.load_question_history(context)
            
            # 7. Build execution context for skill
            skill_context = {
                "student_id": context.student_id,
                "topic": context.additional_context.get("topic", "general"),
                "previous_questions": context.question_history,
                "target_role": context.target_role or context.student_memory.get("target_role", "Software Engineer")
            }
            
            # 8. Execute skill
            logger.info("AssessmentPipeline: Executing AssessmentSkill")
            result = await self.assessment_skill.execute(context=skill_context, schema=AssessmentOutputSchema)
            
            # 9. Validate result
            if not await self.validate_result(result):
                raise ValueError("Assessment skill returned invalid result")
            
            # 10. Extract result data
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
            assessment_result = result_dict.get('result', {})
            
            # 11. Evaluate result
            evaluation = await self.evaluate_result(context, result)
            
            # 12. Create evidence
            evidence = []
            if assessment_result.get('assessment_question'):
                evidence.append({
                    "type": "assessment_question",
                    "question_id": assessment_result['assessment_question'].get('question_id'),
                    "question_text": assessment_result['assessment_question'].get('question'),
                    "skill": assessment_result['assessment_question'].get('skill', 'general'),
                    "timestamp": uuid.uuid4().hex
                })
            
            # 13. Update student memory
            await self.update_student_memory(context, result)
            
            # 14. Update career intelligence
            await self.update_career_intelligence(context, result)
            
            # 15. Determine next action
            next_action, next_action_reason = await self.determine_next_action(context, result)
            
            # 16. Calculate progress
            progress = 0.25  # Assessment progress
            
            # 17. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result=assessment_result,
                evaluation=evaluation,
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"AssessmentPipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"AssessmentPipeline: Execution failed - {str(e)}")
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="assessment",
                next_action_reason="Assessment failed, retrying",
                error_message=str(e)
            )
    
    async def load_skill_instructions(self, context: PipelineContext) -> str:
        """Load assessment instructions."""
        logger.info("AssessmentPipeline: Loading assessment instructions")
        # Instructions are loaded by the AssessmentSkill
        return ""
    
    async def load_question_history(self, context: PipelineContext) -> PipelineContext:
        """Load previous assessment questions for uniqueness checking."""
        logger.info("AssessmentPipeline: Loading question history")
        try:
            previous_questions = await self.question_service.get_previous_questions(
                student_id=context.student_id,
                skill="assessment",
                limit=50
            )
            context.question_history = previous_questions
        except Exception as e:
            logger.warning(f"AssessmentPipeline: Failed to load question history - {e}")
            context.question_history = []
        return context
    
    async def validate_result(self, result: Any) -> bool:
        """Validate assessment result."""
        logger.debug("AssessmentPipeline: Validating result")
        if result is None:
            return False
        
        # Check if result has expected structure
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return 'result' in result_dict
        
        return True
    
    async def evaluate_result(self, context: PipelineContext, result: Any) -> Dict[str, Any]:
        """Evaluate assessment result."""
        logger.info("AssessmentPipeline: Evaluating result")
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        assessment_result = result_dict.get('result', {})
        
        return {
            "assessment_completed": assessment_result.get('assessment_completed', False),
            "question_generated": bool(assessment_result.get('assessment_question')),
            "topic": assessment_result.get('topic', 'general')
        }
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action based on assessment completion."""
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        assessment_result = result_dict.get('result', {})
        assessment_completed = assessment_result.get('assessment_completed', False)
        
        if assessment_completed:
            return "skill_gap", "Assessment completed, moving to skill gap analysis"
        else:
            return "assessment", "Continue assessment to evaluate skills"
