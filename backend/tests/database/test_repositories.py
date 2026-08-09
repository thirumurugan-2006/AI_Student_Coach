"""
Database Tests — Repository Layer.

Tests for:
- UserRepository: create, get, get_by_email, update_last_login
- StudentRepository: create_student_profile, get_by_user_id, update_student_profile
- BaseRepository: get, get_multi, update, delete

Uses the in-memory SQLite test DB from conftest.py.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user_repository import UserRepository, UserCreate, UserUpdate
from repositories.student_repository import StudentRepository, StudentCreate, StudentUpdate

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# UserRepository Tests
# ---------------------------------------------------------------------------

class TestUserRepository:

    async def test_create_user_returns_model(self, db_session: AsyncSession):
        """Creating a user should persist and return a UserModel."""
        repo = UserRepository()
        user_in = UserCreate(name="Alice", email="alice@test.com")

        user = await repo.create(db_session, user_in)

        assert user.id is not None
        assert user.name == "Alice"
        assert user.email == "alice@test.com"
        assert user.is_active is True

    async def test_get_user_by_id(self, db_session: AsyncSession):
        """get() should return the user with matching ID."""
        repo = UserRepository()
        user_in = UserCreate(name="Bob", email="bob@test.com")
        created = await repo.create(db_session, user_in)

        fetched = await repo.get(db_session, created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.email == "bob@test.com"

    async def test_get_user_nonexistent_returns_none(self, db_session: AsyncSession):
        """get() should return None for a non-existent ID."""
        repo = UserRepository()

        result = await repo.get(db_session, "non-existent-id")

        assert result is None

    async def test_get_user_by_email(self, db_session: AsyncSession):
        """get_by_email() should find the user by their email address."""
        repo = UserRepository()
        user_in = UserCreate(name="Carol", email="carol@test.com")
        await repo.create(db_session, user_in)

        result = await repo.get_by_email(db_session, "carol@test.com")

        assert result is not None
        assert result.name == "Carol"

    async def test_get_user_by_email_not_found(self, db_session: AsyncSession):
        """get_by_email() should return None for an unknown email."""
        repo = UserRepository()

        result = await repo.get_by_email(db_session, "nobody@test.com")

        assert result is None

    async def test_update_last_login(self, db_session: AsyncSession):
        """update_last_login() should set the last_login timestamp."""
        repo = UserRepository()
        user_in = UserCreate(name="Dave", email="dave@test.com")
        user = await repo.create(db_session, user_in)

        assert user.last_login is None

        updated = await repo.update_last_login(db_session, user.id)

        assert updated.last_login is not None

    async def test_get_multi_returns_list(self, db_session: AsyncSession):
        """get_multi() should return a list of users."""
        repo = UserRepository()
        await repo.create(db_session, UserCreate(name="User1", email="u1@test.com"))
        await repo.create(db_session, UserCreate(name="User2", email="u2@test.com"))

        users = await repo.get_multi(db_session)

        assert len(users) >= 2

    async def test_delete_user(self, db_session: AsyncSession):
        """delete() should remove the user from the database."""
        repo = UserRepository()
        user_in = UserCreate(name="Temp", email="temp@test.com")
        user = await repo.create(db_session, user_in)

        await repo.delete(db_session, user.id)

        result = await repo.get(db_session, user.id)
        assert result is None


# ---------------------------------------------------------------------------
# StudentRepository Tests
# ---------------------------------------------------------------------------

class TestStudentRepository:

    async def _create_user(self, db, name="Test User", email="test@test.com"):
        """Helper to create a prerequisite user."""
        user_repo = UserRepository()
        return await user_repo.create(db, UserCreate(name=name, email=email))

    async def test_create_student_profile(self, db_session: AsyncSession):
        """create_student_profile() should create a linked student profile."""
        user = await self._create_user(db_session)
        repo = StudentRepository()

        student = await repo.create_student_profile(db_session, user.id)

        assert student is not None
        assert student.user_id == user.id
        assert student.readiness_score == 0.0

    async def test_get_student_by_user_id(self, db_session: AsyncSession):
        """get_by_user_id() should return the student profile for the user."""
        user = await self._create_user(db_session, email="stu@test.com")
        repo = StudentRepository()
        await repo.create_student_profile(db_session, user.id)

        result = await repo.get_by_user_id(db_session, user.id)

        assert result is not None
        assert result.user_id == user.id

    async def test_update_student_profile(self, db_session: AsyncSession):
        """update_student_profile() should persist field changes."""
        user = await self._create_user(db_session, email="upd@test.com")
        repo = StudentRepository()
        await repo.create_student_profile(db_session, user.id)

        update_data = StudentUpdate(
            career_goal="Backend Engineer",
            experience_level="intermediate",
            readiness_score=45.5,
        )
        updated = await repo.update_student_profile(db_session, user.id, update_data)

        assert updated is not None
        assert updated.career_goal == "Backend Engineer"
        assert updated.experience_level == "intermediate"
        assert updated.readiness_score == 45.5
