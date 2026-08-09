"""
Database Initialisation.

Provides create_all_tables() which should be called once at startup
to ensure all SQLAlchemy models are reflected in the database.

For production use Alembic migrations instead of create_all_tables().
"""

from sqlalchemy.ext.asyncio import AsyncEngine

from database.base import Base
from database.session import engine
from core.logger import database_logger

# Import all models so SQLAlchemy metadata is populated
import models.user                  # noqa: F401
import models.student               # noqa: F401
import models.survey                # noqa: F401
import models.assessment            # noqa: F401
import models.interview             # noqa: F401
import models.learning_roadmap      # noqa: F401
import models.reflection            # noqa: F401
import models.progress              # noqa: F401
import models.readiness             # noqa: F401
import models.memory                # noqa: F401
import models.resume                # noqa: F401
import models.project               # noqa: F401
import models.notification          # noqa: F401
import models.placement             # noqa: F401


async def create_all_tables(db_engine: AsyncEngine = None) -> None:
    """
    Create all database tables defined in SQLAlchemy models.

    This is idempotent — tables that already exist are not modified.
    In production, use Alembic migrations for schema changes.

    Args:
        db_engine: Optional engine override (useful for testing).
    """
    target_engine = db_engine or engine
    database_logger.info("Creating database tables...")

    async with target_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    database_logger.info("All database tables created (or already exist)")


async def drop_all_tables(db_engine: AsyncEngine = None) -> None:
    """
    Drop all database tables.

    WARNING: This is destructive. Use only in testing or development.

    Args:
        db_engine: Optional engine override (useful for testing).
    """
    target_engine = db_engine or engine
    database_logger.warning("Dropping ALL database tables!")

    async with target_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    database_logger.warning("All database tables dropped")
