"""
Survey Answer Pipeline

Handles student answers to survey questions.
Processes answers, updates memory, and determines next action.
"""

from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from services.question_service import QuestionService
from core.logger import logger


class SurveyAnswerPipeline(BasePipeline):
    """
    Pipeline for processing survey answers.
    
    Responsible for:
    - Retrieving the question
    - Validating student answer
    - Storing answer
    - Updating survey progress
    - Updating student memory
    - Updating career intelligence
    - Determining whether survey is complete
    - Returning next action
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize SurveyAnswerPipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
        self.question_service = QuestionService()
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Survey Answer Pipeline.
        
        Args:
            context: PipelineContext with student answer information
            
        Returns:
            PipelineResult with next action
        """
        logger.info(f"SurveyAnswerPipeline: Starting execution for student {context.student_id}")
        
        try:
            # 1. Load workflow state
            context = await self.load_workflow_state(context)
            
            # 2. Load student context
            context = await self.load_student_context(context)
            
            # 3. Load career intelligence
            context = await self.load_career_intelligence(context)
            
            # 4. Extract answer from context
            question_id = context.additional_context.get("question_id")
            user_answer = context.additional_context.get("user_answer")
            
            if not question_id or not user_answer:
                raise ValueError("Missing question_id or user_answer in context")
            
            # 5. Retrieve question
            logger.info(f"SurveyAnswerPipeline: Retrieving question {question_id}")
            question = await self.question_service.get_question(question_id)
            if not question:
                raise ValueError(f"Question {question_id} not found")
            
            # 6. Validate student answer
            logger.info("SurveyAnswerPipeline: Validating student answer")
            if not await self.validate_answer(user_answer):
                logger.warning("SurveyAnswerPipeline: Answer validation failed, proceeding anyway")
            
            # 7. Store answer
            logger.info("SurveyAnswerPipeline: Storing answer")
            await self.store_answer(context, question_id, user_answer)
            
            # 8. Update survey progress
            logger.info("SurveyAnswerPipeline: Updating survey progress")
            await self.update_survey_progress(context)
            
            # 9. Update student memory
            logger.info("SurveyAnswerPipeline: Updating student memory")
            await self.update_student_memory_with_answer(context, question, user_answer)
            
            # 10. Update career intelligence
            logger.info("SurveyAnswerPipeline: Updating career intelligence")
            await self.update_career_intelligence_with_answer(context, question, user_answer)
            
            # 11. Determine if survey is complete
            survey_complete = await self.check_survey_completion(context)
            
            # 12. Determine next action
            if survey_complete:
                next_action = "assessment"
                next_action_reason = "Survey completed, moving to assessment"
                progress = 0.2
            else:
                next_action = "survey"
                next_action_reason = "Continue survey to collect more information"
                progress = 0.15
            
            # 13. Create evidence
            evidence = [{
                "type": "survey_answer",
                "question_id": question_id,
                "question_text": question.get("question_text", ""),
                "answer": user_answer,
                "timestamp": context.additional_context.get("timestamp", "")
            }]
            
            # 14. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result={
                    "answer_stored": True,
                    "survey_complete": survey_complete,
                    "question_id": question_id
                },
                evaluation={"survey_complete": survey_complete},
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"SurveyAnswerPipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"SurveyAnswerPipeline: Execution failed - {str(e)}")
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="survey",
                next_action_reason="Survey answer processing failed, retrying",
                error_message=str(e)
            )
    
    async def validate_answer(self, answer: str) -> bool:
        """Validate student answer."""
        logger.debug("SurveyAnswerPipeline: Validating answer")
        # Survey answers are free-form, so basic validation only
        return bool(answer and len(answer.strip()) > 0)
    
    async def store_answer(self, context: PipelineContext, question_id: str, answer: str) -> bool:
        """Store student answer."""
        logger.info(f"SurveyAnswerPipeline: Storing answer for question {question_id}")
        try:
            await self.question_service.store_question_attempt(
                student_id=context.student_id,
                skill="survey",
                question_id=question_id,
                user_answer=answer,
                is_correct=None  # Survey has no correct answers
            )
            return True
        except Exception as e:
            logger.warning(f"SurveyAnswerPipeline: Failed to store answer - {e}")
            return False
    
    async def update_survey_progress(self, context: PipelineContext) -> None:
        """Update survey progress in student memory."""
        logger.info("SurveyAnswerPipeline: Updating survey progress")
        if self.memory and context.student_id:
            profile = context.student_memory or self.memory.get_profile(context.student_id)
            if profile:
                current_progress = profile.get("survey_progress", 0)
                profile["survey_progress"] = current_progress + 1
                context.student_memory = profile
    
    async def update_student_memory_with_answer(self, context: PipelineContext, question: Dict, answer: str) -> bool:
        """Update student memory with answer information."""
        logger.info("SurveyAnswerPipeline: Updating student memory with answer")
        if self.memory and context.student_id:
            profile = context.student_memory or self.memory.get_profile(context.student_id)
            if profile:
                # Extract key information from answer based on question context
                # This is a simplified version - in production, use NLP to extract structured data
                profile["survey_answers"] = profile.get("survey_answers", {})
                profile["survey_answers"][question.get("question_text", "")] = answer
                context.student_memory = profile
                await self.persist_memory(context)
        return True
    
    async def update_career_intelligence_with_answer(self, context: PipelineContext, question: Dict, answer: str) -> bool:
        """Update career intelligence with answer evidence."""
        logger.info("SurveyAnswerPipeline: Updating career intelligence with answer")
        if self.career_intelligence and context.student_id:
            self.career_intelligence.add_evidence(
                context.student_id,
                evidence_type="survey_answer",
                skill="career_discovery",
                score=1.0,
                feedback=answer,
                metadata={
                    "question": question.get("question_text", ""),
                    "answer": answer,
                    "timestamp": context.additional_context.get("timestamp", ""),
                },
            )
        return True
    
    async def check_survey_completion(self, context: PipelineContext) -> bool:
        """Check if survey is complete."""
        logger.info("SurveyAnswerPipeline: Checking survey completion")
        if self.memory and context.student_id:
            profile = context.student_memory or self.memory.get_profile(context.student_id)
            if profile:
                # Survey is complete after 5 questions (as per instructions)
                survey_progress = profile.get("survey_progress", 0)
                return survey_progress >= 5
        return False
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action based on survey completion."""
        survey_complete = await self.check_survey_completion(context)
        
        if survey_complete:
            return "assessment", "Survey completed, moving to assessment"
        else:
            return "survey", "Continue survey to collect more information"
