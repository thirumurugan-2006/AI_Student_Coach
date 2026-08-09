from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import UserModel
from repositories.base import BaseRepository
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    last_login: Optional[str] = None


class UserRepository(BaseRepository[UserModel, UserCreate, UserUpdate]):
    """
    Repository for User operations.
    Simplified for name + email onboarding.
    """

    def __init__(self):
        super().__init__(UserModel)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[UserModel]:
        """Get user by email."""
        return await self.get_by_field(db, "email", email)

    async def update_last_login(self, db: AsyncSession, user_id: str) -> Optional[UserModel]:
        """Update user's last login timestamp."""
        from datetime import datetime, timezone
        user = await self.get(db, user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(user)
        return user
