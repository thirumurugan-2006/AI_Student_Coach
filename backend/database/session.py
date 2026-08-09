from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config.settings import get_settings

settings = get_settings()

# Create the async engine
# For PostgreSQL, we use asyncpg driver
database_url = settings.DATABASE_URL
if database_url.startswith("sqlite") and "+aiosqlite" not in database_url:
    database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")

engine = create_async_engine(
    database_url,
    echo=False,  # Set to True for SQL query logging
    future=True,
)

# Create the async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db():
    """
    Dependency function for FastAPI endpoints to get a DB session.
    Yields an AsyncSession and ensures it is closed after the request.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
