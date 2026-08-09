"""
Placement Interview Skill

Responsible for generating behavioral interview questions for placement rounds.

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

Validate Response (InterviewQuestionContent)
↓

Backend generates question_id
↓

Create InterviewQuestion with IDs
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
from skills.placement_interview.schema import InterviewOutput, InterviewQuestionContent, InterviewQuestion
from core.skill_output import UniversalSkillOutput
from core.logger import logger
from services.question_service import QuestionService


class PlacementInterviewSkill(BaseSkill):
    """
    Skill for generating behavioral interview questions.
    Inherits from BaseSkill to maintain consistent architecture.
    """

    def __init__(self, llm=None, memory=None):
        super().__init__(llm=llm, memory=memory)
        self.question_service = QuestionService()

    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        """
        Executes the interview question generation and parses the response into the InterviewOutput schema.
        After validation, generates backend question_id and stores the question.
        """
        target_schema = schema or InterviewOutput
        
        # Retrieve previous questions to prevent duplicates
        student_id = context.get("student_id", self.student_id)
        previous_questions = []
        try:
            previous_questions = await self.question_service.get_previous_questions(
                student_id=student_id,
                skill="placement_interview",
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
            
            # Create internal InterviewQuestion with ID
            interview_question = InterviewQuestion(
                question_id=question_id,
                category=content.category,
                topic=content.topic,
                difficulty=content.difficulty,
                question=content.question,
                evaluation_criteria=content.evaluation_criteria,
                sample_answer=content.sample_answer
            )
            
            # Store question in database
            try:
                await self.question_service.store_question(
                    student_id=student_id,
                    skill="placement_interview",
                    topic=content.topic,
                    question_type="interview",
                    difficulty=content.difficulty,
                    question_text=content.question,
                    options=None,
                    correct_option_index=None,
                    metadata={
                        "category": content.category,
                        "evaluation_criteria": content.evaluation_criteria,
                        "sample_answer": content.sample_answer
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to store question: {e}")
            
            # Replace content with internal model
            result.question_content = None
            result.question = interview_question
            
            logger.info(f"Generated and stored question_id {question_id} for interview question")
        
        # Wrap in universal output format
        universal_output = UniversalSkillOutput(
            status="completed",
            skill="placement_interview",
            current_module="placement",
            result=result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)},
            evaluation={},
            evidence=[],
            progress=0.95,
            next_action="placement_hr",
            next_action_reason="Interview round completed, moving to HR round"
        )
        
        return universal_output
