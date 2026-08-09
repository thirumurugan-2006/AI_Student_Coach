"""
AI Career Coach Backend
Main Application Entry Point
"""

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    general_exception_handler
)

# -----------------------------
# Database
# -----------------------------
from database.base import Base
from database.session import engine

# -----------------------------
# Models (for table creation)
# -----------------------------
from models.user import UserModel
from models.student import StudentProfileModel

# -----------------------------
# API Routes
# -----------------------------
from api.router import api_router

# -----------------------------
# Core Components
# -----------------------------
from memory.student_memory import StudentMemory
from agent.career_coach import CareerCoach
from agent.placement_simulator import PlacementSimulator
from core.llm_interface import LLMInterface


# ==========================================================
# Application Startup / Shutdown
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the server starts.
    """

    print("========================================")
    print(" Starting AI Career Coach Backend")
    print("========================================")

    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    print(f" Data directory: {data_dir}")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(" Database tables created/verified")

    # Initialize Student Memory Engine
    app.state.memory = StudentMemory()

    # Initialize LLM Interface (Groq)
    try:
        app.state.llm = LLMInterface()
        print(" LLM Interface: Initialized with Groq provider")
    except ValueError as e:
        print(f" ERROR: {e}")
        print(" AI features will not work without a valid GROQ_API_KEY")
        print(" Get a free API key at https://console.groq.com/keys")
        app.state.llm = None  # Set to None to allow startup to continue

    # Check LLM health
    if app.state.llm:
        try:
            llm_health = await app.state.llm.health_check()
            content_healthy = llm_health.get("content_llm", False)
            planning_healthy = llm_health.get("planning_llm", False)
            
            if not content_healthy:
                print(" WARNING: Groq (Content LLM) not reachable. AI features will not work.")
            else:
                print(" Groq (Content LLM) connected successfully")
            
            if not planning_healthy:
                print(" WARNING: Ollama (Planning LLM) not configured. Planning features will use fallback.")
            else:
                print(" Ollama (Planning LLM) connected successfully")
        except Exception as e:
            print(f" WARNING: LLM health check failed: {e}")
            print(" AI features may not work properly")
    else:
        print(" WARNING: LLM Interface not initialized. AI features will not work.")

    # Initialize Main AI Agent and Placement Simulator only if LLM is available
    if app.state.llm:
        app.state.career_agent = CareerCoach(
            memory=app.state.memory,
            llm=app.state.llm
        )

        app.state.placement_simulator = PlacementSimulator(
            memory=app.state.memory,
            llm=app.state.llm
        )

        # Register skills
        from skills.survey.skill import SurveySkill
        from skills.assessment.skill import AssessmentSkill
        from skills.skill_gap.skill import SkillGapSkill
        from skills.roadmap.skill import RoadmapSkill
        from skills.learning.skill import LearningSkill
        from skills.interview.skill import InterviewSkill
        from skills.reflection.skill import ReflectionSkill
        from skills.placement_aptitude.skill import PlacementAptitudeSkill
        from skills.placement_coding.skill import PlacementCodingSkill
        from skills.placement_technical.skill import PlacementTechnicalSkill
        from skills.placement_interview.skill import PlacementInterviewSkill
        from skills.placement_hr.skill import PlacementHRSkill

        # Register pipelines
        from pipelines.register_pipelines import register_all_pipelines
        register_all_pipelines()
        
        # Store pipeline router in app state
        from pipelines.router import pipeline_router
        app.state.pipeline_router = pipeline_router

        app.state.career_agent = CareerCoach(
            memory=app.state.memory,
            llm=app.state.llm,
            pipeline_router=pipeline_router
        )

        app.state.career_agent.register_skill("survey", SurveySkill)
        app.state.career_agent.register_skill("assessment", AssessmentSkill)
        app.state.career_agent.register_skill("skill_gap", SkillGapSkill)
        app.state.career_agent.register_skill("roadmap", RoadmapSkill)
        app.state.career_agent.register_skill("learning", LearningSkill)
        app.state.career_agent.register_skill("interview", InterviewSkill)
        app.state.career_agent.register_skill("reflection", ReflectionSkill)
        app.state.career_agent.register_skill("placement_aptitude", PlacementAptitudeSkill)
        app.state.career_agent.register_skill("placement_coding", PlacementCodingSkill)
        app.state.career_agent.register_skill("placement_technical", PlacementTechnicalSkill)
        app.state.career_agent.register_skill("placement_interview", PlacementInterviewSkill)
        app.state.career_agent.register_skill("placement_hr", PlacementHRSkill)

        print(" Student Memory Loaded")
        print(" Career Coach Initialized")
        print(" Placement Simulator Initialized")
        print(" All Skills Registered")
    else:
        print(" WARNING: Career Coach and Placement Simulator not initialized (no LLM)")
        print(" AI features will not be available")

    yield

    print(" Shutting down...")


# ==========================================================
# FastAPI App
# ==========================================================

app = FastAPI(
    title="AI Career Coach API",
    description="Personalized AI Career Coach & Interview Preparation System",
    version="1.0.0",
    lifespan=lifespan
)

# ==========================================================
# Exception Handlers
# ==========================================================

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "detail": exc.errors(),
            "path": str(request.url.path)
        }
    )

app.add_exception_handler(RequestValidationError, validation_exception_handler)

# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Register API Routes
# ==========================================================

app.include_router(api_router)

# ==========================================================
# Root Endpoint
# ==========================================================

@app.get("/")
async def root():
    return {
        "application": "AI Career Coach",
        "version": "1.0.0",
        "status": "Running",
        "agent": "Career Coach",
        "memory": "Student Memory Engine",
        "message": "Welcome to AI Career Coach API — visit /docs for API documentation"
    }


# ==========================================================
# Health Check Endpoint
# ==========================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and frontend connectivity.
    """
    llm_status = "not_configured"
    planning_llm_status = "not_configured"
    
    if getattr(app.state, 'llm', None):
        try:
            llm_health = await app.state.llm.health_check()
            llm_status = "connected" if llm_health.get("content_llm", False) else "not_configured"
            planning_llm_status = "connected" if llm_health.get("planning_llm", False) else "not_configured"
        except Exception:
            llm_status = "error"
            planning_llm_status = "error"
    
    agent_status = "ready" if getattr(app.state, 'career_agent', None) else "not_initialized"
    
    return {
        "status": "healthy",
        "service": "AI Career Coach Backend",
        "database": "SQLite",
        "content_llm": llm_status,
        "planning_llm": planning_llm_status,
        "backend": "online",
        "memory": "loaded",
        "agent": agent_status
    }