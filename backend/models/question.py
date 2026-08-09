"""
Question and Question History Models

Stores generated questions, attempts, and history to prevent duplicates.
"""

from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Integer, Float, Text
from datetime import datetime, timezone
from database.base import Base


class QuestionModel(Base):
    """
    SQLAlchemy model for storing generated questions.
    """
    __tablename__ = "questions"

    id = Column(String, primary_key=True, index=True)
    question_id = Column(String, unique=True, index=True, nullable=False)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), nullable=False, index=True)
    skill = Column(String, nullable=False, index=True)
    topic = Column(String, nullable=False, index=True)
    question_type = Column(String, nullable=False)  # mcq, coding, technical, interview, hr
    difficulty = Column(String, nullable=False)  # easy, medium, hard
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # For MCQ questions
    correct_option_index = Column(Integer, nullable=True)  # For MCQ questions
    question_metadata = Column(JSON, default=dict)  # Renamed from 'metadata' to avoid SQLAlchemy reserved name
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    is_active = Column(Integer, default=1)  # Soft delete flag


class QuestionAttemptModel(Base):
    """
    SQLAlchemy model for storing student question attempts.
    """
    __tablename__ = "question_attempts"

    id = Column(String, primary_key=True, index=True)
    attempt_id = Column(String, unique=True, index=True, nullable=False)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), nullable=False, index=True)
    question_id = Column(String, ForeignKey("questions.question_id"), nullable=False, index=True)
    skill = Column(String, nullable=False, index=True)
    answer = Column(Text, nullable=True)
    selected_option = Column(Integer, nullable=True)  # For MCQ
    is_correct = Column(Integer, nullable=True)  # 1 for correct, 0 for incorrect, null for subjective
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    time_taken_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
