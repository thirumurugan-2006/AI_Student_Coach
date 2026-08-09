from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Integer
from datetime import datetime, timezone
from database.base import Base

class ProgressModel(Base):
    """
    SQLAlchemy model for Student Progress tracking.
    """
    __tablename__ = "progress"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), nullable=False)
    total_study_hours = Column(Integer, default=0)
    topics_completed = Column(Integer, default=0)
    assessments_completed = Column(Integer, default=0)
    interviews_completed = Column(Integer, default=0)
    reflections_completed = Column(Integer, default=0)
    milestones = Column(JSON, default=list)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
