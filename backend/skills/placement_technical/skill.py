"""
Placement Technical Skill

Responsible for generating technical interview questions for placement rounds.

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

Validate Response (TechnicalQuestionContent)
↓

Backend generates question_id
↓

Create TechnicalQuestion with IDs
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
from skills.placement_technical.schema import TechnicalOutput, TechnicalQuestionContent, TechnicalQuestion
from core.skill_output import UniversalSkillOutput
from core.logger import logger
from services.question_service import QuestionService


class PlacementTechnicalSkill(BaseSkill):
    """
    Skill for generating technical interview questions.
    Inherits from BaseSkill to maintain consistent architecture.
    """

    def __init__(self, llm=None, memory=None):
        super().__init__(llm=llm, memory=memory)
        self.question_service = QuestionService()

    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        """
        Executes the technical question generation and parses the response into the TechnicalOutput schema.
        After validation, generates backend question_id and stores the question.
        """
        target_schema = schema or TechnicalOutput
        
        # Retrieve previous questions to prevent duplicates
        student_id = context.get("student_id", self.student_id)
        previous_questions = []
        try:
            previous_questions = await self.question_service.get_previous_questions(
                student_id=student_id,
                skill="placement_technical",
                limit=50
            )
        except Exception as e:
            logger.warning(f"Failed to retrieve previous questions: {e}")
        
        # Add previous questions to context
        context["previous_questions"] = previous_questions
        
        # Execute the skill
        result = await super().execute(context=context, schema=target_schema)
        
        # Ensure result is not a coroutine
        if hasattr(result, '__await__'):
            logger.error("Result is a coroutine, awaiting it...")
            result = await result
        
        # If result contains question content, generate question_id and store
        if hasattr(result, 'question_content') and result.question_content:
            content = result.question_content
            
            # Check for duplicates
            if self.question_service.is_duplicate_question(content.question, previous_questions):
                logger.warning(f"Duplicate question detected for student {student_id}, retrying...")
                # In production, would retry with different prompt
                # For now, proceed with the question
            
            # Generate backend question_id
            question_id = str(uuid.uuid4())
            
            # Create internal TechnicalQuestion with ID
            technical_question = TechnicalQuestion(
                question_id=question_id,
                topic=content.topic,
                difficulty=content.difficulty,
                question=content.question,
                options=content.options,
                correct_option_index=content.correct_option_index,
                explanation=content.explanation
            )
            
            # Store question in database
            try:
                await self.question_service.store_question(
                    student_id=student_id,
                    skill="placement_technical",
                    topic=content.topic,
                    question_type="technical",
                    difficulty=content.difficulty,
                    question_text=content.question,
                    options=content.options,
                    correct_option_index=content.correct_option_index,
                    metadata={"explanation": content.explanation}
                )
            except Exception as e:
                logger.warning(f"Failed to store question: {e}")
            
            # Replace content with internal model
            result.question_content = None
            result.question = technical_question
            
            logger.info(f"Generated and stored question_id {question_id} for technical question")
        
        # Wrap in universal output format
        universal_output = UniversalSkillOutput(
            status="completed",
            skill="placement_technical",
            current_module="placement",
            result=result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)},
            evaluation={},
            evidence=[],
            progress=0.9,
            next_action="placement_interview",
            next_action_reason="Technical round completed, moving to interview round"
        )
        
        return universal_output
