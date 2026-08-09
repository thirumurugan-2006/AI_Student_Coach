from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Float
from datetime import datetime, timezone
from database.base import Base

class ReflectionModel(Base):
    """
    SQLAlchemy model for Reflection sessions.
    """
    __tablename__ = "reflections"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), nullable=False)
    reflection_response = Column(String, nullable=False)
    insights = Column(JSON, default=list)
    confidence_score = Column(Float, default=0.0)
    learning_points = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
