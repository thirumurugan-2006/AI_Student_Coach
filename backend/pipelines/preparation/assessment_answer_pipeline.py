"""
Assessment Answer Pipeline

Handles student answers to assessment questions.
Processes answers, evaluates performance, and determines next action.
"""

from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from services.question_service import QuestionService
from core.logger import logger


class AssessmentAnswerPipeline(BasePipeline):
    """
    Pipeline for processing assessment answers.
    
    Responsible for:
    - Retrieving the question
    - Retrieving the correct answer
    - Evaluating student performance
    - Storing attempt
    - Calculating performance metrics
    - Creating skill evidence
    - Updating career intelligence
    - Updating memory
    - Checking assessment completion
    - Returning next action
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize AssessmentAnswerPipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
        self.question_service = QuestionService()
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Assessment Answer Pipeline.
        
        Args:
            context: PipelineContext with student answer information
            
        Returns:
            PipelineResult with next action
        """
        logger.info(f"AssessmentAnswerPipeline: Starting execution for student {context.student_id}")
        
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
            logger.info(f"AssessmentAnswerPipeline: Retrieving question {question_id}")
            question = await self.question_service.get_question(question_id)
            if not question:
                raise ValueError(f"Question {question_id} not found")
            
            # 6. Retrieve correct answer
            logger.info("AssessmentAnswerPipeline: Retrieving correct answer")
            correct_option_index = question.get("correct_option_index")
            
            # 7. Evaluate answer
            logger.info("AssessmentAnswerPipeline: Evaluating answer")
            is_correct = await self.evaluate_answer(user_answer, correct_option_index)
            
            # 8. Store attempt
            logger.info("AssessmentAnswerPipeline: Storing attempt")
            await self.store_attempt(context, question_id, user_answer, is_correct)
            
            # 9. Calculate performance
            logger.info("AssessmentAnswerPipeline: Calculating performance")
            performance = await self.calculate_performance(context)
            
            # 10. Create skill evidence
            logger.info("AssessmentAnswerPipeline: Creating skill evidence")
            evidence = await self.create_evidence(context, question, user_answer, is_correct)
            
            # 11. Update career intelligence
            logger.info("AssessmentAnswerPipeline: Updating career intelligence")
            await self.update_career_intelligence_with_evidence(context, evidence)
            
            # 12. Update student memory
            logger.info("AssessmentAnswerPipeline: Updating student memory")
            await self.update_student_memory_with_performance(context, performance)
            
            # 13. Check assessment completion
            logger.info("AssessmentAnswerPipeline: Checking assessment completion")
            assessment_complete = await self.check_assessment_completion(context)
            
            # 14. Determine next action
            if assessment_complete:
                next_action = "skill_gap"
                next_action_reason = "Assessment completed, moving to skill gap analysis"
                progress = 0.3
            else:
                next_action = "assessment"
                next_action_reason = "Continue assessment to evaluate more skills"
                progress = 0.27
            
            # 15. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result={
                    "answer_stored": True,
                    "is_correct": is_correct,
                    "assessment_complete": assessment_complete,
                    "question_id": question_id
                },
                evaluation=performance,
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"AssessmentAnswerPipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"AssessmentAnswerPipeline: Execution failed - {str(e)}")
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="assessment",
                next_action_reason="Assessment answer processing failed, retrying",
                error_message=str(e)
            )
    
    async def evaluate_answer(self, user_answer: str, correct_option_index: int) -> bool:
        """Evaluate student answer against correct answer."""
        logger.debug("AssessmentAnswerPipeline: Evaluating answer")
        try:
            # Convert user_answer to integer if it's a string
            if isinstance(user_answer, str):
                user_answer = int(user_answer.strip())
            return user_answer == correct_option_index
        except (ValueError, TypeError):
            logger.warning(f"AssessmentAnswerPipeline: Could not parse answer '{user_answer}'")
            return False
    
    async def store_attempt(self, context: PipelineContext, question_id: str, user_answer: str, is_correct: bool) -> bool:
        """Store assessment attempt."""
        logger.info(f"AssessmentAnswerPipeline: Storing attempt for question {question_id}")
        try:
            await self.question_service.store_question_attempt(
                student_id=context.student_id,
                skill="assessment",
                question_id=question_id,
                user_answer=user_answer,
                is_correct=is_correct
            )
            return True
        except Exception as e:
            logger.warning(f"AssessmentAnswerPipeline: Failed to store attempt - {e}")
            return False
    
    async def calculate_performance(self, context: PipelineContext) -> Dict[str, Any]:
        """Calculate assessment performance metrics."""
        logger.info("AssessmentAnswerPipeline: Calculating performance")
        try:
            attempts = await self.question_service.get_student_attempts(
                student_id=context.student_id,
                skill="assessment"
            )
            
            if not attempts:
                return {"total_attempts": 0, "correct_answers": 0, "accuracy": 0.0}
            
            total_attempts = len(attempts)
            correct_answers = sum(1 for attempt in attempts if attempt.get("is_correct"))
            accuracy = (correct_answers / total_attempts) * 100 if total_attempts > 0 else 0.0
            
            return {
                "total_attempts": total_attempts,
                "correct_answers": correct_answers,
                "accuracy": round(accuracy, 2)
            }
        except Exception as e:
            logger.warning(f"AssessmentAnswerPipeline: Failed to calculate performance - {e}")
            return {"total_attempts": 0, "correct_answers": 0, "accuracy": 0.0}
    
    async def create_evidence(self, context: PipelineContext, question: Dict, user_answer: str, is_correct: bool) -> list:
        """Create skill evidence from assessment answer."""
        logger.info("AssessmentAnswerPipeline: Creating skill evidence")
        return [{
            "type": "assessment_answer",
            "question_id": question.get("question_id"),
            "question_text": question.get("question_text"),
            "skill": question.get("metadata", {}).get("skill", "general"),
            "user_answer": user_answer,
            "is_correct": is_correct,
            "timestamp": context.additional_context.get("timestamp", "")
        }]
    
    async def update_career_intelligence_with_evidence(self, context: PipelineContext, evidence: list) -> bool:
        """Update career intelligence with assessment evidence."""
        logger.info("AssessmentAnswerPipeline: Updating career intelligence with evidence")
        if self.career_intelligence and context.student_id:
            for ev in evidence:
                self.career_intelligence.add_evidence(
                    context.student_id,
                    evidence_type=ev.get("type", "assessment_answer"),
                    skill=ev.get("skill", "general"),
                    score=1.0 if ev.get("is_correct") else 0.0,
                    is_correct=ev.get("is_correct"),
                    metadata=ev,
                )
        return True
    
    async def update_student_memory_with_performance(self, context: PipelineContext, performance: Dict) -> bool:
        """Update student memory with assessment performance."""
        logger.info("AssessmentAnswerPipeline: Updating student memory with performance")
        if self.memory and context.student_id:
            profile = context.student_memory or self.memory.get_profile(context.student_id)
            if profile:
                profile["assessment_performance"] = performance
                context.student_memory = profile
                await self.persist_memory(context)
        return True
    
    async def check_assessment_completion(self, context: PipelineContext) -> bool:
        """Check if assessment is complete."""
        logger.info("AssessmentAnswerPipeline: Checking assessment completion")
        try:
            attempts = await self.question_service.get_student_attempts(
                student_id=context.student_id,
                skill="assessment"
            )
            # Assessment is complete after 10 questions
            return len(attempts) >= 10
        except Exception as e:
            logger.warning(f"AssessmentAnswerPipeline: Failed to check completion - {e}")
            return False
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action based on assessment completion."""
        assessment_complete = await self.check_assessment_completion(context)
        
        if assessment_complete:
            return "skill_gap", "Assessment completed, moving to skill gap analysis"
        else:
            return "assessment", "Continue assessment to evaluate more skills"
