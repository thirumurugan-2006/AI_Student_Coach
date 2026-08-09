from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from datetime import datetime, timezone
from database.base import Base

class InterviewHistoryModel(Base):
    """
    SQLAlchemy model tracking interview simulations for a student.
    """
    __tablename__ = "interview_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), nullable=False)
    conducted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    company = Column(String, nullable=True)
    role = Column(String, nullable=True)
    questions_asked = Column(JSON, default=list)
    feedback = Column(JSON, default=dict)
    overall_score = Column(Integer, default=0)

class ReflectionHistoryModel(Base):
    """
    SQLAlchemy model tracking student self-reflections.
    """
    __tablename__ = "reflection_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    confidence_level = Column(String, nullable=False)
    reflection_notes = Column(String, nullable=True)
    suggested_action = Column(String, nullable=True)
