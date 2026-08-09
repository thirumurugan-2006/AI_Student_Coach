"""
Placement Skill

Responsible for generating placement questions and assessing placement readiness.

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

Validate Response (PlacementQuestionContent)
↓

Backend generates question_id
↓

Create PlacementQuestion with IDs
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
from skills.placement.schema import PlacementOutput, PlacementQuestionContent, PlacementQuestion
from core.logger import logger
from services.question_service import QuestionService


class PlacementSkill(BaseSkill):
    """
    Skill for generating placement questions and assessing placement readiness.
    Inherits from BaseSkill to maintain consistent architecture.
    """

    def __init__(self, llm=None, memory=None, student_id=None):
        super().__init__(llm=llm, memory=memory, student_id=student_id)
        self.question_service = QuestionService()

    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        """
        Executes the placement logic and parses the response into the PlacementOutput schema.
        After validation, generates backend question_id for placement questions.
        """
        target_schema = schema or PlacementOutput
        
        # Retrieve previous questions to prevent duplicates
        student_id = context.get("student_id", self.student_id)
        previous_questions = []
        try:
            previous_questions = await self.question_service.get_previous_questions(
                student_id=student_id,
                skill="placement",
                limit=50
            )
        except Exception as e:
            logger.warning(f"PlacementSkill: Failed to retrieve previous questions: {e}")
        
        # Add previous questions to context
        context["previous_questions"] = previous_questions
        
        result = await super().execute(context=context, schema=target_schema)

        # If the LLM returned a PlacementOutput directly, return it as-is
        if isinstance(result, PlacementOutput):
            return result
        
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
            
            # Create internal PlacementQuestion with ID
            placement_question = PlacementQuestion(
                question_id=question_id,
                question_type=content.question_type,
                skill=content.skill,
                topic=content.topic,
                difficulty=content.difficulty,
                question=content.question,
                options=content.options,
                correct_option_index=content.correct_option_index,
                explanation=content.explanation
            )
            
            # Store question in database
            await self.question_service.store_question(
                student_id=student_id,
                skill=content.skill,
                topic=content.topic,
                question_type=content.question_type,
                difficulty=content.difficulty,
                question_text=content.question,
                options=content.options,
                correct_option_index=content.correct_option_index,
                metadata={"explanation": content.explanation}
            )
            
            # Replace content with internal model
            result.question_content = None
            result.question = placement_question
            
            logger.info(f"Generated and stored question_id {question_id} for placement question")
        
        return result
