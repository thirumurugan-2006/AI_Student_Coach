from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Float
from datetime import datetime, timezone
from database.base import Base

class AssessmentModel(Base):
    """
    SQLAlchemy model for Technical Skill Assessment.
    """
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), nullable=False)
    topic = Column(String, nullable=False)
    questions = Column(JSON, default=list)
    answers = Column(JSON, default=list)
    topic_evaluations = Column(JSON, default=dict)
    score = Column(Float, default=0.0)
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
