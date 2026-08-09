"""
Core FastAPI Dependencies.

Centralises dependency injection for:
- Database sessions
- Current user authentication
- Career Coach agent from app state
- Student memory from app state
"""

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from auth.jwt_handler import JWTHandler
from repositories.user_repository import UserRepository
from core.logger import logger

# ---------------------------------------------------------------------------
# Re-export get_db so callers can import from core.dependencies
# ---------------------------------------------------------------------------
__all__ = [
    "get_db",
    "get_current_user",
    "get_current_student_id",
    "get_career_agent",
    "get_student_memory",
    "get_optional_current_user",
]

security = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Authentication Dependencies
# ---------------------------------------------------------------------------

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Resolve the currently authenticated user from the Bearer JWT token.

    Raises:
        HTTPException 401: If token is missing or invalid.
        HTTPException 403: If the user account is inactive.
        HTTPException 404: If the user no longer exists in the database.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    user_id = JWTHandler.verify_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository()
    user = await user_repo.get(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    logger.debug(f"Authenticated user: {user.id}")
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_active": user.is_active,
    }


async def get_current_student_id(
    current_user: dict = Depends(get_current_user),
) -> str:
    """
    Extract student ID from the authenticated user dict.
    Student ID is identical to User ID in this system.
    """
    return current_user["id"]


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> dict | None:
    """
    Resolve the current user if a token is present, otherwise return None.
    Useful for endpoints that have both public and authenticated modes.
    """
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials=credentials, db=db)
    except HTTPException:
        return None


# ---------------------------------------------------------------------------
# App State Dependencies
# ---------------------------------------------------------------------------

def get_career_agent(request: Request):
    """
    Return the CareerCoach instance initialised in the lifespan startup.

    Raises:
        HTTPException 503: If the agent is not initialised.
    """
    agent = getattr(request.app.state, "career_agent", None)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Career Coach agent is not initialised",
        )
    return agent


def get_student_memory(request: Request):
    """
    Return the StudentMemory instance initialised in the lifespan startup.

    Raises:
        HTTPException 503: If memory is not initialised.
    """
    memory = getattr(request.app.state, "memory", None)
    if memory is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Student memory is not initialised",
        )
    return memory
