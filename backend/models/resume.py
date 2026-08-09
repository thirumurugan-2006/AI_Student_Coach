from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from datetime import datetime, timezone
from database.base import Base

class ResumeModel(Base):
    """
    SQLAlchemy model for Student Resume data.
    """
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), unique=True, nullable=False)
    content = Column(JSON, default=dict)
    skills = Column(JSON, default=list)
    experience = Column(JSON, default=list)
    education = Column(JSON, default=list)
    file_path = Column(String, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
