"""
Assessment Skill

Skill for analyzing memory, generating adaptive assessments,
and evaluating answers dynamically.

Workflow

Read Memory
↓

Load Instruction
↓

Build Prompt
↓

Retrieve Previous Questions (QuestionService)
↓

Call LLM
↓

Validate Response (AssessmentQuestionContent)
↓

Backend generates question_id
↓

Create AssessmentQuestion with IDs
↓

Store Question (QuestionService)
↓

Update Memory
↓

Return Result
"""

import uuid
from typing import Dict, Any
from core.base_skill import BaseSkill
from skills.assessment.schema import AssessmentOutputSchema, AssessmentQuestionContent, AssessmentQuestion
from core.skill_output import UniversalSkillOutput
from core.logger import logger
from services.question_service import QuestionService


class AssessmentSkill(BaseSkill):
    """
    Skill for analyzing memory, generating adaptive assessments,
    and evaluating answers dynamically.
    """
    
    def __init__(self, llm=None, memory=None):
        super().__init__(llm=llm, memory=memory)
        self.question_service = QuestionService()
    
    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        """
        Executes the assessment logic and parses the response into the AssessmentOutputSchema.
        After validation, generates backend question_id and stores the question.
        Returns UniversalSkillOutput for consistent API responses.
        """
        # Override the default schema if none provided, ensuring strict parsing.
        target_schema = schema or AssessmentOutputSchema
        
        # Retrieve previous questions to prevent duplicates
        student_id = context.get("student_id", self.student_id)
        previous_questions = []
        try:
            previous_questions = await self.question_service.get_previous_questions(
                student_id=student_id,
                skill="assessment",
                limit=50
            )
        except Exception as e:
            logger.warning(f"Failed to retrieve previous questions: {e}")
        
        # Add previous questions to context
        context["previous_questions"] = previous_questions
        
        # BaseSkill's execute handles building prompt with memory, instructions, examples.
        result = await super().execute(context=context, schema=target_schema)
        
        # Ensure result is not a coroutine
        if hasattr(result, '__await__'):
            logger.error("Result is a coroutine, awaiting it...")
            result = await result
        
        # If result contains question content, generate question_id and store
        if hasattr(result, 'next_question_content') and result.next_question_content:
            content = result.next_question_content
            
            # Check for duplicates
            if self.question_service.is_duplicate_question(content.question, previous_questions):
                logger.warning(f"Duplicate question detected for student {student_id}, retrying...")
                # In production, would retry with different prompt
                # For now, proceed with the question
            
            # Generate backend question_id
            question_id = str(uuid.uuid4())
            
            # Create internal AssessmentQuestion with ID
            assessment_question = AssessmentQuestion(
                question_id=question_id,
                question=content.question,
                options=content.options,
                correct_option_index=content.correct_option_index,
                explanation=content.explanation
            )
            
            # Store question in database
            try:
                await self.question_service.store_question(
                    student_id=student_id,
                    skill="assessment",
                    topic=context.get("topic", "general"),
                    question_type="mcq",
                    difficulty=context.get("difficulty", "medium"),
                    question_text=content.question,
                    options=content.options,
                    correct_option_index=content.correct_option_index,
                    metadata={"explanation": content.explanation}
                )
            except Exception as e:
                logger.warning(f"Failed to store question: {e}")
            
            # Replace content with internal model
            result.next_question_content = None
            result.next_question = assessment_question
            
            logger.info(f"Generated and stored question_id {question_id} for assessment question")
        
        # Wrap in universal output format
        assessment_completed = result.assessment_completed if hasattr(result, 'assessment_completed') else False
        next_action = "skill_gap" if assessment_completed else "assessment"
        next_action_reason = "Assessment completed, moving to skill gap analysis" if assessment_completed else "Continue assessment"
        
        universal_output = UniversalSkillOutput(
            status="completed",
            skill="assessment",
            current_module="preparation",
            result=result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)},
            evaluation={},
            evidence=[],
            progress=0.2 if not assessment_completed else 0.3,
            next_action=next_action,
            next_action_reason=next_action_reason
        )
        
        return universal_output
