"""
Memory Persistence Service.

Bridges the in-memory StudentMemory (fast, request-scoped)
with the persistent SQLite/PostgreSQL database.

Responsibilities:
- Load student profile from DB into memory at session start
- Flush in-memory changes back to DB after skill execution
- Keep memory and DB in sync
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from memory.student_memory import StudentMemory
from repositories.student_repository import StudentRepository, StudentUpdate
from core.logger import logger


class MemoryPersistenceService:
    """
    Synchronises the in-memory StudentMemory with the persistent database.

    The Career Coach works exclusively with the in-memory store for speed.
    This service handles loading from and flushing back to the database.
    """

    def __init__(self, memory: StudentMemory):
        self.memory = memory
        self.student_repo = StudentRepository()

    async def load_from_db(self, db: AsyncSession, user_id: str) -> None:
        """
        Load a student's persisted profile from the database into memory.

        Called once when a user authenticates to populate the in-memory store.

        Args:
            db: Active database session.
            user_id: The user/student ID.
        """
        db_profile = await self.student_repo.get_by_user_id(db, user_id)

        if not db_profile:
            logger.warning(f"No DB profile found for user {user_id}. Memory will start fresh.")
            return

        # Ensure student exists in memory
        if not self.memory.get_profile(user_id):
            self.memory.create_student(user_id, "Loaded from DB")

        mem_profile = self.memory.get_profile(user_id)

        # Sync fields from DB → memory
        mem_profile["career_goal"] = db_profile.career_goal
        mem_profile["target_company"] = db_profile.target_company
        mem_profile["experience_level"] = db_profile.experience_level
        mem_profile["study_hours"] = db_profile.study_hours or 0
        mem_profile["learning_style"] = db_profile.learning_style
        mem_profile["skills"] = db_profile.skills or {}
        mem_profile["knowledge_graph"] = db_profile.knowledge_graph or {}
        mem_profile["roadmap"] = db_profile.roadmap or []
        mem_profile["completed_topics"] = db_profile.completed_topics or []
        mem_profile["weak_topics"] = db_profile.weak_topics or []
        mem_profile["strong_topics"] = db_profile.strong_topics or []
        mem_profile["readiness_score"] = db_profile.readiness_score or 0.0

        logger.info(f"Loaded DB profile for user {user_id} into memory")

    async def flush_to_db(self, db: AsyncSession, user_id: str) -> None:
        """
        Flush the current in-memory profile back to the database.

        Called after skill execution to persist any changes made by the
        Evaluation Engine.

        Args:
            db: Active database session.
            user_id: The user/student ID.
        """
        mem_profile = self.memory.get_profile(user_id)
        if not mem_profile:
            logger.warning(f"No memory profile for user {user_id}. Nothing to flush.")
            return

        update_data = StudentUpdate(
            career_goal=mem_profile.get("career_goal"),
            target_company=mem_profile.get("target_company"),
            experience_level=mem_profile.get("experience_level"),
            study_hours=mem_profile.get("study_hours", 0),
            learning_style=mem_profile.get("learning_style"),
            skills=mem_profile.get("skills", {}),
            knowledge_graph=mem_profile.get("knowledge_graph", {}),
            roadmap=mem_profile.get("roadmap", []),
            completed_topics=mem_profile.get("completed_topics", []),
            weak_topics=mem_profile.get("weak_topics", []),
            strong_topics=mem_profile.get("strong_topics", []),
            readiness_score=mem_profile.get("readiness_score", 0.0),
        )

        await self.student_repo.update_student_profile(db, user_id, update_data)
        logger.info(f"Flushed memory profile for user {user_id} to DB")

    async def sync(self, db: AsyncSession, user_id: str) -> None:
        """
        Convenience method: load from DB, then flush back any merged changes.
        Used on re-authentication to refresh memory with latest DB state.
        """
        await self.load_from_db(db, user_id)
        logger.info(f"Memory sync complete for user {user_id}")
