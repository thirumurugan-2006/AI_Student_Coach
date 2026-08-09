from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from datetime import datetime, timezone
from database.base import Base

class ReadinessScoreModel(Base):
    """
    SQLAlchemy model for Industry Readiness Score.
    """
    __tablename__ = "readiness_scores"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), unique=True, nullable=False)
    overall_score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
