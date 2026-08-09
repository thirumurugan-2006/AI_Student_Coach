from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from repositories.user_repository import UserRepository, UserCreate
from repositories.student_repository import StudentRepository
from auth.password_handler import PasswordHandler
from auth.jwt_handler import JWTHandler
from core.logger import logger, auth_logger

router = APIRouter()


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    google_id: str
    email: EmailStr
    full_name: str
    profile_picture: str = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    full_name: str
    email: str
    provider: str


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new user with email/password.
    Automatically creates student profile and initializes memory.
    """
    user_repo = UserRepository()
    
    # Check if user already exists
    existing_user = await user_repo.get_by_email(db, request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = PasswordHandler.hash_password(request.password)
    
    # Create user with auto-generated UUID
    user_in = UserCreate(
        full_name=request.full_name,
        email=request.email,
        password_hash=password_hash,
        provider="email"
    )
    
    try:
        user = await user_repo.create(db, user_in)
        logger.info(f"User registered: {user.email}")
        
        # Create student profile automatically
        student_repo = StudentRepository()
        student_profile = await student_repo.create_student_profile(db, user.id)
        logger.info(f"Student profile created for user: {user.id}")
        
        # Initialize student memory
        from memory.student_memory import StudentMemory
        memory = StudentMemory()
        await memory.initialize_student(db, user.id)
        logger.info(f"Student memory initialized for user: {user.id}")
        
        # Generate access token
        access_token = JWTHandler.create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
            provider=user.provider
        )
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate a user with email/password and return an access token.
    """
    user_repo = UserRepository()
    
    # Get user by email
    user = await user_repo.get_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not PasswordHandler.verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update last login
    await user_repo.update_last_login(db, user.id)
    
    # Generate access token
    access_token = JWTHandler.create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    
    auth_logger.info(f"User logged in: {user.email}")
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        provider=user.provider
    )


@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate or register a user via Google OAuth.
    Automatically creates student profile and initializes memory for new users.
    """
    user_repo = UserRepository()
    
    # Check if user exists by Google ID
    existing_user = await user_repo.get_by_google_id(db, request.google_id)
    
    if existing_user:
        # User exists, log them in
        await user_repo.update_last_login(db, existing_user.id)
        access_token = JWTHandler.create_access_token(
            data={"sub": existing_user.id, "email": existing_user.email}
        )
        auth_logger.info(f"User logged in via Google: {existing_user.email}")
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=existing_user.id,
            full_name=existing_user.full_name,
            email=existing_user.email,
            provider=existing_user.provider
        )
    
    # Check if email already exists with different provider
    email_user = await user_repo.get_by_email(db, request.email)
    if email_user:
        raise HTTPException(status_code=400, detail="Email already registered with different provider")
    
    # Create new user from Google
    user_in = UserCreate(
        full_name=request.full_name,
        email=request.email,
        google_id=request.google_id,
        provider="google",
        profile_picture=request.profile_picture
    )
    
    try:
        user = await user_repo.create(db, user_in)
        logger.info(f"User registered via Google: {user.email}")
        
        # Create student profile automatically
        student_repo = StudentRepository()
        student_profile = await student_repo.create_student_profile(db, user.id)
        logger.info(f"Student profile created for Google user: {user.id}")
        
        # Initialize student memory
        from memory.student_memory import StudentMemory
        memory = StudentMemory()
        await memory.initialize_student(db, user.id)
        logger.info(f"Student memory initialized for Google user: {user.id}")
        
        # Generate access token
        access_token = JWTHandler.create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
            provider=user.provider
        )
    except Exception as e:
        logger.error(f"Google authentication failed: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")


@router.post("/demo", response_model=AuthResponse)
async def demo_mode(db: AsyncSession = Depends(get_db)):
    """
    Demo mode for testing without registration.
    Creates a temporary demo user and logs them in.
    """
    user_repo = UserRepository()
    
    # Try to find existing demo user
    demo_email = "demo@careercoach.ai"
    existing_user = await user_repo.get_by_email(db, demo_email)
    
    if existing_user:
        # Log in existing demo user
        await user_repo.update_last_login(db, existing_user.id)
        access_token = JWTHandler.create_access_token(
            data={"sub": existing_user.id, "email": existing_user.email}
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=existing_user.id,
            full_name=existing_user.full_name,
            email=existing_user.email,
            provider="demo"
        )
    
    # Create new demo user
    import uuid
    demo_password = PasswordHandler.hash_password("demo123")
    
    user_in = UserCreate(
        full_name="Demo User",
        email=demo_email,
        password_hash=demo_password,
        provider="demo"
    )
    
    try:
        user = await user_repo.create(db, user_in)
        logger.info(f"Demo user created: {user.email}")
        
        # Create student profile automatically
        student_repo = StudentRepository()
        student_profile = await student_repo.create_student_profile(db, user.id)
        logger.info(f"Student profile created for demo user: {user.id}")
        
        # Initialize student memory
        from memory.student_memory import StudentMemory
        memory = StudentMemory()
        await memory.initialize_student(db, user.id)
        logger.info(f"Student memory initialized for demo user: {user.id}")
        
        # Generate access token
        access_token = JWTHandler.create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
            provider=user.provider
        )
    except Exception as e:
        logger.error(f"Demo mode failed: {e}")
        raise HTTPException(status_code=500, detail="Demo mode failed")


@router.post("/logout")
async def logout():
    """
    Logout endpoint (JWT tokens are stateless, frontend handles token removal).
    """
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user(token: str, db: AsyncSession = Depends(get_db)):
    """
    Get the current user from the token.
    """
    user_id = JWTHandler.verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_repo = UserRepository()
    user = await user_repo.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "provider": user.provider,
        "profile_picture": user.profile_picture,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "last_login": user.last_login
    }
