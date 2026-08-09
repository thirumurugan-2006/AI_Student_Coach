from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Float
from datetime import datetime, timezone
from database.base import Base

class InterviewModel(Base):
    """
    SQLAlchemy model for Mock Interview sessions.
    """
    __tablename__ = "interviews"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), nullable=False)
    company_name = Column(String, nullable=True)
    job_role = Column(String, nullable=True)
    questions = Column(JSON, default=list)
    answers = Column(JSON, default=list)
    feedback = Column(JSON, default=dict)
    overall_score = Column(Float, default=0.0)
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
