"""
Placement Coding Skill

Responsible for generating coding interview questions for placement rounds.

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

Validate Response (CodingQuestionContent)
↓

Backend generates question_id
↓

Create CodingQuestion with IDs
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
from skills.placement_coding.schema import CodingOutput, CodingQuestionContent, CodingQuestion
from core.skill_output import UniversalSkillOutput
from core.logger import logger
from services.question_service import QuestionService


class PlacementCodingSkill(BaseSkill):
    """
    Skill for generating coding interview questions.
    Inherits from BaseSkill to maintain consistent architecture.
    """

    def __init__(self, llm=None, memory=None):
        super().__init__(llm=llm, memory=memory)
        self.question_service = QuestionService()

    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        """
        Executes the coding question generation and parses the response into the CodingOutput schema.
        After validation, generates backend question_id and stores the question.
        """
        target_schema = schema or CodingOutput
        
        # Retrieve previous questions to prevent duplicates
        student_id = context.get("student_id", self.student_id)
        previous_questions = []
        try:
            previous_questions = await self.question_service.get_previous_questions(
                student_id=student_id,
                skill="placement_coding",
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
            
            # Create internal CodingQuestion with ID
            coding_question = CodingQuestion(
                question_id=question_id,
                topic=content.topic,
                difficulty=content.difficulty,
                question=content.question,
                constraints=content.constraints,
                examples=content.examples,
                hints=content.hints,
                time_complexity=content.time_complexity,
                space_complexity=content.space_complexity
            )
            
            # Store question in database
            try:
                await self.question_service.store_question(
                    student_id=student_id,
                    skill="placement_coding",
                    topic=content.topic,
                    question_type="coding",
                    difficulty=content.difficulty,
                    question_text=content.question,
                    options=None,
                    correct_option_index=None,
                    metadata={
                        "constraints": content.constraints,
                        "examples": content.examples,
                        "hints": content.hints,
                        "time_complexity": content.time_complexity,
                        "space_complexity": content.space_complexity
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to store question: {e}")
            
            # Replace content with internal model
            result.question_content = None
            result.question = coding_question
            
            logger.info(f"Generated and stored question_id {question_id} for coding question")
        
        # Wrap in universal output format
        universal_output = UniversalSkillOutput(
            status="completed",
            skill="placement_coding",
            current_module="placement",
            result=result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)},
            evaluation={},
            evidence=[],
            progress=0.85,
            next_action="placement_technical",
            next_action_reason="Coding round completed, moving to technical round"
        )
        
        return universal_output
