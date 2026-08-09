from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime, timezone
from database.base import Base
import uuid

class UserModel(Base):
    """
    Simplified SQLAlchemy model for User.
    Only requires name and email for onboarding.
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)
