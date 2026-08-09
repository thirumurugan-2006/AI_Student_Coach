"""
Survey Skill

Responsible for generating survey questions for career discovery.

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

Validate Response (SurveyQuestionContent)

↓

Create MCQQuestion with IDs

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
from skills.survey.schema import SurveyOutput, SurveyQuestionContent, MCQQuestion
from core.skill_output import UniversalSkillOutput
from core.logger import logger
from services.question_service import QuestionService


class SurveySkill(BaseSkill):
    """
    Skill for generating survey questions.
    Inherits from BaseSkill to maintain consistent architecture.
    """

    def __init__(self, llm=None, memory=None):
        super().__init__(llm=llm, memory=memory)
        self.question_service = QuestionService()

    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        """
        Executes the survey question generation and parses the response into the SurveyOutput schema.
        After validation, generates backend question_id and stores the question.
        Returns UniversalSkillOutput for consistent API responses.
        """
        target_schema = schema or SurveyOutput
        logger.info(f"SurveySkill: Starting execution, target schema: {target_schema}")
        logger.info(f"SurveySkill: Context: {context}")
        
        # Retrieve previous questions to prevent duplicates
        student_id = context.get("student_id", self.student_id)
        logger.info(f"SurveySkill: Student ID: {student_id}")
        previous_questions = []
        try:
            previous_questions = await self.question_service.get_previous_questions(
                student_id=student_id,
                skill="survey",
                limit=50
            )
            logger.info(f"SurveySkill: Retrieved {len(previous_questions)} previous questions")
        except Exception as e:
            logger.warning(f"SurveySkill: Failed to retrieve previous questions: {e}")
        
        # Add previous questions to context
        context["previous_questions"] = previous_questions
        
        # Execute the skill
        logger.info("SurveySkill: Calling super().execute()")
        try:
            result = await super().execute(context=context, schema=target_schema)
            logger.info(f"SurveySkill: super().execute() returned type: {type(result)}")
            if isinstance(result, SurveyOutput):
                return result
        except Exception as e:
            logger.error(f"SurveySkill: super().execute() failed with error: {e}", exc_info=True)
            raise
        
        # Ensure result is not a coroutine
        if hasattr(result, '__await__'):
            logger.error("Result is a coroutine, awaiting it...")
            result = await result
            logger.debug(f"SurveySkill: After await, result type: {type(result)}")
        
        # If result contains question content, generate question_id and store
        if hasattr(result, 'mcq_question_content') and result.mcq_question_content:
            content = result.mcq_question_content
            
            # Check for duplicates
            if self.question_service.is_duplicate_question(content.question, previous_questions):
                logger.warning(f"Duplicate question detected for student {student_id}, retrying...")
                # In production, would retry with different prompt
                # For now, proceed with the question
            
            # Generate backend question_id
            question_id = str(uuid.uuid4())
            
            # Create internal MCQQuestion with ID
            mcq_question = MCQQuestion(
                question_id=question_id,
                question=content.question,
                options=content.options,
                explanation=content.explanation
            )
            
            # Store question in database
            try:
                await self.question_service.store_question(
                    student_id=student_id,
                    skill="survey",
                    topic="career_discovery",
                    question_type="mcq",
                    difficulty="easy",
                    question_text=content.question,
                    options=content.options,
                    correct_option_index=None,  # Survey has no correct answer
                    metadata={"explanation": content.explanation}
                )
            except Exception as e:
                logger.warning(f"Failed to store question: {e}")
            
            # Replace content with internal model
            result.mcq_question_content = None
            result.mcq_question = mcq_question
            
            logger.info(f"Generated and stored question_id {question_id} for survey question")
        
        # Wrap in universal output format
        survey_completed = result.survey_completed if hasattr(result, 'survey_completed') else False
        next_action = "assessment" if survey_completed else "survey"
        next_action_reason = "Survey completed, moving to assessment" if survey_completed else "Continue survey"
        
        logger.debug(f"SurveySkill: Creating UniversalSkillOutput with result type: {type(result)}")
        universal_output = UniversalSkillOutput(
            status="completed",
            skill="survey",
            current_module="preparation",
            result=result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)},
            evaluation={},
            evidence=[],
            progress=0.1 if not survey_completed else 0.2,
            next_action=next_action,
            next_action_reason=next_action_reason
        )
        logger.debug(f"SurveySkill: UniversalSkillOutput created, type: {type(universal_output)}")
        
        return universal_output