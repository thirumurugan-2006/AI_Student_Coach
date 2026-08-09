"""
Test Configuration and Shared Fixtures.

Provides:
- Async test database session (SQLite in-memory)
- FastAPI test client
- Mock Career Coach agent
- Mock student memory
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from unittest.mock import AsyncMock, MagicMock

from database.base import Base
from database.session import get_db
from memory.student_memory import StudentMemory


# ---------------------------------------------------------------------------
# Test Database Setup
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Provide a clean in-memory SQLite session for each test.
    Creates all tables before the test, drops them after.
    """
    # Import all models to populate metadata
    import models.user          # noqa
    import models.student       # noqa

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------------
# FastAPI Test Client
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    """
    Provide an async HTTP test client with the test database injected.
    """
    from main import app

    # Override the real DB dependency with test DB
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Set up mock app state
    mock_memory = StudentMemory()
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(return_value="mock LLM response")
    mock_llm.health_check = AsyncMock(return_value=True)

    mock_agent = MagicMock()
    mock_agent.handle_request = AsyncMock(return_value={"message": "mock response"})
    mock_agent.registry._skills = {}

    app.state.memory = mock_memory
    app.state.llm = mock_llm
    app.state.career_agent = mock_agent

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Shared Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_memory():
    """Fresh StudentMemory instance for unit tests."""
    memory = StudentMemory()
    memory.create_student("test-student-001", "Test Student")
    return memory


@pytest.fixture
def mock_llm():
    """Mock LLMInterface that returns a preset response."""
    llm = MagicMock()
    llm.generate = AsyncMock(return_value="mock response")
    llm.health_check = AsyncMock(return_value=True)
    return llm


@pytest.fixture
def sample_student_id():
    return "test-student-001"
