"""
Question Service

Manages question generation, history, and duplicate detection.
"""

import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from database.session import AsyncSessionLocal
from models.question import QuestionModel, QuestionAttemptModel
from core.logger import logger


class QuestionService:
    """
    Service for managing question generation and history.
    Prevents duplicate questions and maintains question lifecycle.
    """

    def __init__(self):
        pass

    async def get_previous_questions(
        self,
        student_id: str,
        skill: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve previous questions for a student and skill to prevent duplicates.
        
        Args:
            student_id: The student's ID
            skill: The skill/topic area
            limit: Maximum number of questions to retrieve
            
        Returns:
            List of previous question dictionaries
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(QuestionModel)
                .where(
                    and_(
                        QuestionModel.student_id == student_id,
                        QuestionModel.skill == skill,
                        QuestionModel.is_active == 1
                    )
                )
                .order_by(QuestionModel.created_at.desc())
                .limit(limit)
            )
            questions = result.scalars().all()
            
            return [
                {
                    "question_id": q.question_id,
                    "question_text": q.question_text,
                    "topic": q.topic,
                    "question_type": q.question_type,
                    "difficulty": q.difficulty,
                    "options": q.options,
                    "created_at": q.created_at.isoformat() if q.created_at else None
                }
                for q in questions
            ]

    async def store_question(
        self,
        student_id: str,
        skill: str,
        topic: str,
        question_type: str,
        difficulty: str,
        question_text: str,
        options: Optional[List[str]] = None,
        correct_option_index: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store a generated question in the database.
        
        Args:
            student_id: The student's ID
            skill: The skill/topic area
            topic: The specific topic within the skill
            question_type: Type of question (mcq, coding, technical, etc.)
            difficulty: Difficulty level (easy, medium, hard)
            question_text: The question text
            options: List of options for MCQ questions
            correct_option_index: Index of correct option for MCQ
            metadata: Additional metadata
            
        Returns:
            The question_id of the stored question
        """
        question_id = str(uuid.uuid4())
        id = str(uuid.uuid4())
        
        async with AsyncSessionLocal() as session:
            question = QuestionModel(
                id=id,
                question_id=question_id,
                student_id=student_id,
                skill=skill,
                topic=topic,
                question_type=question_type,
                difficulty=difficulty,
                question_text=question_text,
                options=options,
                correct_option_index=correct_option_index,
                question_metadata=metadata or {}
            )
            session.add(question)
            await session.commit()
            
        logger.info(f"Stored question {question_id} for student {student_id}, skill {skill}")
        return question_id

    async def store_attempt(
        self,
        student_id: str,
        question_id: str,
        skill: str,
        answer: Optional[str] = None,
        selected_option: Optional[int] = None,
        is_correct: Optional[bool] = None,
        score: Optional[float] = None,
        feedback: Optional[str] = None,
        time_taken_seconds: Optional[int] = None
    ) -> str:
        """
        Store a student's attempt at a question.
        
        Args:
            student_id: The student's ID
            question_id: The question's ID
            skill: The skill/topic area
            answer: The student's answer text
            selected_option: Selected option index for MCQ
            is_correct: Whether the answer was correct
            score: Score for the attempt
            feedback: Feedback on the attempt
            time_taken_seconds: Time taken to answer
            
        Returns:
            The attempt_id of the stored attempt
        """
        attempt_id = str(uuid.uuid4())
        id = str(uuid.uuid4())
        
        async with AsyncSessionLocal() as session:
            attempt = QuestionAttemptModel(
                id=id,
                attempt_id=attempt_id,
                student_id=student_id,
                question_id=question_id,
                skill=skill,
                answer=answer,
                selected_option=selected_option,
                is_correct=1 if is_correct else 0 if is_correct is not None else None,
                score=score,
                feedback=feedback,
                time_taken_seconds=time_taken_seconds
            )
            session.add(attempt)
            await session.commit()
            
        logger.info(f"Stored attempt {attempt_id} for question {question_id}, student {student_id}")
        return attempt_id

    def is_duplicate_question(
        self,
        new_question: str,
        previous_questions: List[Dict[str, Any]],
        similarity_threshold: float = 0.85
    ) -> bool:
        """
        Check if a new question is too similar to previous questions.
        
        Args:
            new_question: The new question text to check
            previous_questions: List of previous question dictionaries
            similarity_threshold: Threshold for considering as duplicate (0-1)
            
        Returns:
            True if the question is likely a duplicate, False otherwise
        """
        if not new_question or not previous_questions:
            return False
        
        # Simple normalized text comparison
        # For production, consider using embedding-based similarity
        
        new_normalized = self._normalize_question(new_question)
        
        for prev_q in previous_questions:
            if not prev_q or "question_text" not in prev_q:
                continue
                
            prev_normalized = self._normalize_question(prev_q["question_text"])
            
            # Exact match
            if new_normalized == prev_normalized:
                logger.warning(f"Duplicate question detected: {new_question[:50]}...")
                return True
            
            # Check for high similarity (simple word overlap for now)
            similarity = self._calculate_similarity(new_normalized, prev_normalized)
            if similarity >= similarity_threshold:
                logger.warning(f"Similar question detected (similarity={similarity:.2f}): {new_question[:50]}...")
                return True
        
        return False

    def _normalize_question(self, question: str) -> str:
        """Normalize question text for comparison."""
        if not question:
            return ""
        # Lowercase, remove extra whitespace, remove punctuation
        normalized = question.lower().strip()
        # Remove common punctuation
        for char in ".,!?;:":
            normalized = normalized.replace(char, "")
        # Normalize multiple spaces
        while "  " in normalized:
            normalized = normalized.replace("  ", " ")
        return normalized

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using word overlap.
        Simple implementation - consider using embeddings for production.
        """
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

    async def get_question_stats(
        self,
        student_id: str,
        skill: str
    ) -> Dict[str, Any]:
        """
        Get statistics about questions for a student and skill.
        
        Args:
            student_id: The student's ID
            skill: The skill/topic area
            
        Returns:
            Dictionary with question statistics
        """
        async with AsyncSessionLocal() as session:
            # Count total questions
            result = await session.execute(
                select(QuestionModel)
                .where(
                    and_(
                        QuestionModel.student_id == student_id,
                        QuestionModel.skill == skill,
                        QuestionModel.is_active == 1
                    )
                )
            )
            total_questions = len(result.scalars().all())
            
            # Count attempts
            result = await session.execute(
                select(QuestionAttemptModel)
                .where(
                    and_(
                        QuestionAttemptModel.student_id == student_id,
                        QuestionAttemptModel.skill == skill
                    )
                )
            )
            total_attempts = len(result.scalars().all())
            
            # Calculate average score
            result = await session.execute(
                select(QuestionAttemptModel.score)
                .where(
                    and_(
                        QuestionAttemptModel.student_id == student_id,
                        QuestionAttemptModel.skill == skill,
                        QuestionAttemptModel.score.isnot(None)
                    )
                )
            )
            scores = result.scalars().all()
            avg_score = sum(scores) / len(scores) if scores else 0.0
            
            return {
                "total_questions": total_questions,
                "total_attempts": total_attempts,
                "average_score": avg_score
            }
