from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, ForeignKey
from datetime import datetime, timezone
from database.base import Base
import uuid

class StudentProfileModel(Base):
    """
    SQLAlchemy model for the core Student Profile.
    Automatically created after user registration.
    Linked to User via user_id.
    """
    __tablename__ = "student_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Career Profile
    career_goal = Column(String, nullable=True)
    target_company = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    study_hours = Column(Integer, default=0)
    learning_style = Column(String, nullable=True)
    resume_path = Column(String, nullable=True)
    
    # JSON Fields for dynamic flexible schemas (skills, knowledge graph)
    skills = Column(JSON, default=dict)
    knowledge_graph = Column(JSON, default=dict)
    
    roadmap = Column(JSON, default=list)
    completed_topics = Column(JSON, default=list)
    weak_topics = Column(JSON, default=list)
    strong_topics = Column(JSON, default=list)
    
    readiness_score = Column(Float, default=0.0)
