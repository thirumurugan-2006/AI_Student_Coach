from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from repositories.user_repository import UserRepository
from repositories.student_repository import StudentRepository
from auth.jwt_handler import JWTHandler
from core.logger import logger

router = APIRouter()


class UserSignupRequest(BaseModel):
    name: str
    email: str


class UserSessionResponse(BaseModel):
    user_id: str
    name: str
    email: str
    is_new_user: bool
    message: str
    access_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    user_id: str
    name: str
    email: str
    created_at: str
    last_login: str


@router.post("/signup", response_model=UserSessionResponse)
async def user_signup(
    request: Request,
    payload: UserSignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Simplified user signup - only requires name and email.
    Creates or loads existing user, initializes student memory.
    """
    user_repo = UserRepository()
    
    # Validate email format
    if "@" not in payload.email or "." not in payload.email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Check if user exists
    existing_user = await user_repo.get_by_email(db, payload.email)
    
    if existing_user:
        # Load existing user
        await user_repo.update_last_login(db, existing_user.id)
        logger.info(f"Existing user logged in: {existing_user.email}")
        
        # Load student memory
        memory = request.app.state.memory
        await memory.initialize_student(db, existing_user.id, existing_user.name)
        
        access_token = JWTHandler.create_access_token(
            data={"sub": existing_user.id, "email": existing_user.email}
        )

        return UserSessionResponse(
            user_id=existing_user.id,
            name=existing_user.name,
            email=existing_user.email,
            is_new_user=False,
            message="Welcome back! Your profile has been loaded.",
            access_token=access_token,
        )
    
    # Create new user
    from repositories.user_repository import UserCreate
    user_in = UserCreate(
        name=payload.name,
        email=payload.email
    )
    
    try:
        user = await user_repo.create(db, user_in)
        logger.info(f"New user created: {user.email}")
        
        # Create student profile automatically
        student_repo = StudentRepository()
        student_profile = await student_repo.create_student_profile(db, user.id)
        logger.info(f"Student profile created for user: {user.id}")
        
        # Initialize student memory
        memory = request.app.state.memory
        await memory.initialize_student(db, user.id, user.name)
        logger.info(f"Student memory initialized for user: {user.id}")
        
        access_token = JWTHandler.create_access_token(
            data={"sub": user.id, "email": user.email}
        )

        return UserSessionResponse(
            user_id=user.id,
            name=user.name,
            email=user.email,
            is_new_user=True,
            message="Account created successfully! Welcome to AI Career Coach.",
            access_token=access_token,
        )
    except Exception as e:
        logger.error(f"User signup failed: {e}")
        raise HTTPException(status_code=500, detail="Signup failed")


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user profile by user_id.
    """
    user_repo = UserRepository()
    user = await user_repo.get(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfileResponse(
        user_id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at.isoformat() if user.created_at else "",
        last_login=user.last_login.isoformat() if user.last_login else ""
    )


@router.get("/session")
async def get_user_session(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user session info.
    """
    user_repo = UserRepository()
    user = await user_repo.get(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "is_active": user.is_active,
        "last_login": user.last_login.isoformat() if user.last_login else None
    }


@router.post("/logout")
async def user_logout(user_id: str):
    """
    Logout endpoint (session management handled by frontend).
    """
    logger.info(f"User logged out: {user_id}")
    return {"message": "Successfully logged out"}
