from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.student import StudentProfileModel
from repositories.base import BaseRepository
from pydantic import BaseModel


class StudentCreate(BaseModel):
    user_id: str


class StudentUpdate(BaseModel):
    career_goal: Optional[str] = None
    target_company: Optional[str] = None
    experience_level: Optional[str] = None
    study_hours: Optional[int] = None
    learning_style: Optional[str] = None
    resume_path: Optional[str] = None
    skills: Optional[dict] = None
    knowledge_graph: Optional[dict] = None
    roadmap: Optional[list] = None
    completed_topics: Optional[list] = None
    weak_topics: Optional[list] = None
    strong_topics: Optional[list] = None
    readiness_score: Optional[float] = None


class StudentRepository(BaseRepository[StudentProfileModel, StudentCreate, StudentUpdate]):
    """
    Repository for Student Profile operations.
    Linked to User via user_id.
    """

    def __init__(self):
        super().__init__(StudentProfileModel)

    async def get_by_user_id(self, db: AsyncSession, user_id: str) -> Optional[StudentProfileModel]:
        """Get student profile by user ID."""
        result = await db.execute(
            select(StudentProfileModel).where(StudentProfileModel.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_student_profile(self, db: AsyncSession, user_id: str) -> StudentProfileModel:
        """Create a new student profile for a user."""
        student_in = StudentCreate(user_id=user_id)
        return await self.create(db, student_in)

    async def update_student_profile(
        self, 
        db: AsyncSession, 
        user_id: str, 
        update_data: StudentUpdate
    ) -> Optional[StudentProfileModel]:
        """Update student profile by user ID."""
        db_obj = await self.get_by_user_id(db, user_id)
        if db_obj:
            return await self.update(db, db_obj, update_data)
        return None
