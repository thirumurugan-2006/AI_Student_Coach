from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from datetime import datetime, timezone
from database.base import Base

class LearningRoadmapModel(Base):
    """
    SQLAlchemy model for Personalized Learning Roadmap.
    """
    __tablename__ = "learning_roadmaps"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), nullable=False)
    roadmap = Column(JSON, default=list)
    current_topic = Column(String, nullable=True)
    completed_topics = Column(JSON, default=list)
    weak_topics = Column(JSON, default=list)
    strong_topics = Column(JSON, default=list)
    resources = Column(JSON, default=list)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
