from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from datetime import datetime, timezone
from database.base import Base

class ProjectModel(Base):
    """
    SQLAlchemy model for Student Projects.
    """
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    technologies = Column(JSON, default=list)
    status = Column(String, default="in_progress")
    github_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
