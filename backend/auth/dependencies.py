from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from auth.jwt_handler import JWTHandler
from repositories.user_repository import UserRepository

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials containing the JWT token.
        db: Database session.
        
    Returns:
        User dictionary if authenticated.
        
    Raises:
        HTTPException: If token is invalid or user not found.
    """
    token = credentials.credentials
    user_id = JWTHandler.verify_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_repo = UserRepository()
    user = await user_repo.get(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_active": user.is_active
    }


async def get_current_student_id(
    current_user: dict = Depends(get_current_user)
) -> str:
    """
    Dependency to get the current student ID from authenticated user.
    
    Args:
        current_user: Current authenticated user.
        
    Returns:
        Student ID string.
    """
    return current_user["id"]
