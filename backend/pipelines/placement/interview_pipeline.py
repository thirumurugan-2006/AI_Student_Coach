"""
Interview Pipeline

Handles behavioral interview questions for placement simulation.
Generates interview questions based on resume, projects, and skills.
"""

import uuid
from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from skills.placement_interview.skill import PlacementInterviewSkill
from skills.placement_interview.schema import InterviewOutput
from services.question_service import QuestionService
from core.logger import logger


class InterviewPipeline(BasePipeline):
    """
    Pipeline for Interview skill execution.
    
    Responsible for:
    - Loading resume/project evidence
    - Loading skills and target role
    - Loading weak areas
    - Loading previous interview history
    - Generating interview questions via Groq
    - Validating responses
    - Storing questions with backend-generated IDs
    - Checking for duplicates
    - Returning structured results
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize InterviewPipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
        self.question_service = QuestionService()
        self.interview_skill = PlacementInterviewSkill(llm=llm, memory=memory)
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Interview Pipeline.
        
        Args:
            context: PipelineContext with student information
            
        Returns:
            PipelineResult with interview question
        """
        logger.info(f"InterviewPipeline: Starting execution for student {context.student_id}")
        
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
                "resume_evidence": context.student_memory.get("resume", {}),
                "projects": context.student_memory.get("projects", []),
                "skills": context.student_memory.get("skills", {}),
                "weak_areas": context.student_memory.get("weak_skills", []),
                "previous_questions": context.question_history,
                "placement_performance": context.student_memory.get("placement_performance", {})
            }
            
            # 7. Execute skill
            logger.info("InterviewPipeline: Executing PlacementInterviewSkill")
            result = await self.interview_skill.execute(context=skill_context, schema=InterviewOutput)
            
            # 8. Validate result
            if not await self.validate_result(result):
                raise ValueError("Interview skill returned invalid result")
            
            # 9. Extract result data
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
            interview_result = result_dict.get('result', {})
            
            # 10. Evaluate result
            evaluation = await self.evaluate_result(context, result)
            
            # 11. Create evidence
            evidence = []
            if interview_result.get('interview_question'):
                evidence.append({
                    "type": "interview_question",
                    "question_id": interview_result['interview_question'].get('question_id'),
                    "question_text": interview_result['interview_question'].get('question'),
                    "question_type": interview_result['interview_question'].get('question_type', 'behavioral'),
                    "timestamp": uuid.uuid4().hex
                })
            
            # 12. Update student memory
            await self.update_student_memory(context, result)
            
            # 13. Update career intelligence
            await self.update_career_intelligence(context, result)
            
            # 14. Determine next action
            next_action, next_action_reason = await self.determine_next_action(context, result)
            
            # 15. Calculate progress
            progress = 0.95  # Interview progress
            
            # 16. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result=interview_result,
                evaluation=evaluation,
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"InterviewPipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"InterviewPipeline: Execution failed - {str(e)}")
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="placement_interview",
                next_action_reason="Interview question generation failed, retrying",
                error_message=str(e)
            )
    
    async def load_question_history(self, context: PipelineContext) -> PipelineContext:
        """Load previous interview questions for uniqueness checking."""
        logger.info("InterviewPipeline: Loading question history")
        try:
            previous_questions = await self.question_service.get_previous_questions(
                student_id=context.student_id,
                skill="placement_interview",
                limit=50
            )
            context.question_history = previous_questions
        except Exception as e:
            logger.warning(f"InterviewPipeline: Failed to load question history - {e}")
            context.question_history = []
        return context
    
    async def validate_result(self, result: Any) -> bool:
        """Validate interview result."""
        logger.debug("InterviewPipeline: Validating result")
        if result is None:
            return False
        
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return 'result' in result_dict
        
        return True
    
    async def evaluate_result(self, context: PipelineContext, result: Any) -> Dict[str, Any]:
        """Evaluate interview result."""
        logger.info("InterviewPipeline: Evaluating result")
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        interview_result = result_dict.get('result', {})
        
        return {
            "interview_completed": interview_result.get('interview_completed', False),
            "question_generated": bool(interview_result.get('interview_question')),
            "question_type": interview_result.get('interview_question', {}).get('question_type', 'behavioral')
        }
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action based on interview completion."""
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        interview_result = result_dict.get('result', {})
        interview_completed = interview_result.get('interview_completed', False)
        
        if interview_completed:
            return "placement_hr", "Interview round completed, moving to HR round"
        else:
            return "placement_interview", "Continue interview"
