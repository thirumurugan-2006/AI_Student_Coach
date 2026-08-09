from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from datetime import datetime, timezone
from database.base import Base

class SurveyModel(Base):
    """
    SQLAlchemy model for Career Survey data.
    """
    __tablename__ = "surveys"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), nullable=False)
    career_goal = Column(String, nullable=True)
    target_company = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    study_hours = Column(String, nullable=True)
    learning_style = Column(String, nullable=True)
    interests = Column(JSON, default=list)
    responses = Column(JSON, default=dict)
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
