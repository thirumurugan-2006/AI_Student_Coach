from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from datetime import datetime, timezone
from database.base import Base

class NotificationModel(Base):
    """
    SQLAlchemy model for User Notifications.
    """
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    notification_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
