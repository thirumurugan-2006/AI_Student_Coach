"""
Health Check Command
Checks system health and component availability
"""
import sys
import asyncio
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))


def health_command(args):
    """Execute health check command"""
    print("=" * 40)
    print("SYSTEM HEALTH")
    print("=" * 40)
    print()
    
    results = {}
    
    # Check Environment
    results['Environment'] = check_environment()
    
    # Check Database
    results['Database'] = check_database()
    
    # Check Groq
    results['Groq'] = check_groq()
    
    # Check Qwen
    results['Qwen'] = check_qwen()
    
    # Check Workflow
    results['Workflow'] = check_workflow()
    
    # Check Router
    results['Router'] = check_router()
    
    # Check Pipeline
    results['Pipeline'] = check_pipeline()
    
    # Check Survey
    results['Survey'] = check_survey()
    
    # Check Assessment
    results['Assessment'] = check_assessment()
    
    # Check Learning
    results['Learning'] = check_learning()
    
    # Check Placement
    results['Placement'] = check_placement()
    
    # Display results
    all_passed = True
    for component, (status, message) in results.items():
        symbol = "✓" if status else "✗"
        print(f"{component:<16} {symbol}")
        if not status and message:
            print(f"  Error: {message}")
        all_passed = all_passed and status
    
    print()
    if all_passed:
        print("System Status: READY")
        return 0
    else:
        print("System Status: NOT READY")
        return 1


def check_environment():
    """Check environment variables and paths"""
    try:
        # Check if .env exists
        env_path = Path(__file__).parent.parent.parent / '.env'
        if not env_path.exists():
            return False, ".env file not found"
        
        # Check data directory
        data_dir = Path(__file__).parent.parent.parent / 'data'
        if not data_dir.exists():
            return False, "data directory not found"
        
        return True, None
    except Exception as e:
        return False, str(e)


def check_database():
    """Check database connectivity"""
    try:
        from database.session import engine
        from sqlalchemy import text
        import asyncio
        
        async def test_db():
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        
        result = asyncio.run(test_db())
        if result:
            return True, None
        else:
            return False, "Database query failed"
    except Exception as e:
        return False, str(e)


def check_groq():
    """Check Groq API connectivity"""
    try:
        from core.llm_interface import LLMInterface
        import asyncio
        
        async def test_groq():
            llm = LLMInterface()
            health = await llm.health_check()
            return health.get("content_llm", False)
        
        result = asyncio.run(test_groq())
        if result:
            return True, None
        else:
            return False, "Groq health check failed"
    except Exception as e:
        return False, str(e)


def check_qwen():
    """Check Qwen/Ollama connectivity"""
    try:
        from services.ollama_service import OllamaService
        import asyncio
        
        async def test_qwen():
            ollama = OllamaService()
            health = await ollama.health_check()
            if isinstance(health, bool):
                return health
            return health.get("available", False)
        
        result = asyncio.run(test_qwen())
        if result:
            return True, None
        else:
            return False, "Qwen health check failed"
    except Exception as e:
        return False, str(e)


def check_workflow():
    """Check Workflow Controller"""
    try:
        from core.workflow_controller import workflow_controller
        # Just check if it can be imported and initialized
        return True, None
    except Exception as e:
        return False, str(e)


def check_router():
    """Check Pipeline Router"""
    try:
        from pipelines.router import PipelineRouter
        # Create a new router instance for CLI
        router = PipelineRouter()
        # Check if it can be created
        return True, None
    except Exception as e:
        return False, str(e)


def check_pipeline():
    """Check Pipeline availability"""
    try:
        from pipelines.preparation.survey_pipeline import SurveyPipeline
        # Just check if it can be imported
        return True, None
    except Exception as e:
        return False, str(e)


def check_survey():
    """Check Survey Skill"""
    try:
        from skills.survey.skill import SurveySkill
        # Just check if it can be imported
        return True, None
    except Exception as e:
        return False, str(e)


def check_assessment():
    """Check Assessment Skill"""
    try:
        from skills.assessment.skill import AssessmentSkill
        # Just check if it can be imported
        return True, None
    except Exception as e:
        return False, str(e)


def check_learning():
    """Check Learning Skill"""
    try:
        from skills.learning.skill import LearningSkill
        # Just check if it can be imported
        return True, None
    except Exception as e:
        return False, str(e)


def check_placement():
    """Check Placement Skills"""
    try:
        from skills.placement_aptitude.skill import PlacementAptitudeSkill
        from skills.placement_coding.skill import PlacementCodingSkill
        # Just check if they can be imported
        return True, None
    except Exception as e:
        return False, str(e)
