"""
Database Seed Script.

Populates the database with initial test / demo data for development.

Usage:
    python -m database.seed

Or call seed_database() from your startup code in DEBUG mode.
"""

import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from database.session import AsyncSessionLocal
from database.init_db import create_all_tables
from models.user import UserModel
from models.student import StudentProfileModel
from core.logger import database_logger


SEED_USERS = [
    {
        "name": "Alice Dev",
        "email": "alice@example.com",
    },
    {
        "name": "Bob Engineer",
        "email": "bob@example.com",
    },
]


async def _create_seed_user(
    session: AsyncSession, name: str, email: str
) -> UserModel:
    """Create a seed user if they don't already exist."""
    from sqlalchemy import select

    result = await session.execute(select(UserModel).where(UserModel.email == email))
    existing = result.scalar_one_or_none()

    if existing:
        database_logger.info(f"Seed user already exists: {email}")
        return existing

    user = UserModel(id=str(uuid.uuid4()), name=name, email=email)
    session.add(user)
    await session.flush()

    # Create associated student profile
    student = StudentProfileModel(id=str(uuid.uuid4()), user_id=user.id)
    session.add(student)

    database_logger.info(f"Created seed user: {email} (id={user.id})")
    return user


async def seed_database() -> None:
    """
    Seed the database with demo users and student profiles.
    Safe to run multiple times — skips existing records.
    """
    await create_all_tables()

    async with AsyncSessionLocal() as session:
        async with session.begin():
            for user_data in SEED_USERS:
                await _create_seed_user(session, **user_data)

    database_logger.info("Database seeding complete")


if __name__ == "__main__":
    asyncio.run(seed_database())
