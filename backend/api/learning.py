from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
from auth.dependencies import get_current_student_id
from pipelines.pipeline_result import PipelineResult
from core.skill_output import UniversalSkillOutput
from core.logger import logger

router = APIRouter()

class LearningRequest(BaseModel):
    topic_request: str

class LearningResponse(BaseModel):
    result: Dict[str, Any]

@router.post("/", response_model=LearningResponse)
async def generate_learning_roadmap(
    request: Request, 
    payload: LearningRequest,
    student_id: str = Depends(get_current_student_id)
):
    """
    Endpoint for generating and updating the personalized learning roadmap.
    """
    try:
        career_agent = getattr(request.app.state, 'career_agent', None)
        if not career_agent:
            raise HTTPException(
                status_code=503, 
                detail="AI features not available. GROQ_API_KEY is not configured. Please configure the API key in backend/.env"
            )
        
        context = {
            "requested_topic": payload.topic_request
        }
        
        result = await career_agent.handle_request(
            student_id=student_id,
            skill_name="learning",
            context=context
        )
        
        # Ensure result is not a coroutine
        if hasattr(result, '__await__'):
            logger.error("Result is a coroutine, awaiting it...")
            result = await result
        
        # Handle PipelineResult format (new pipeline architecture)
        if isinstance(result, PipelineResult):
            result_dict = result.model_dump()
            return LearningResponse(result=result_dict)
        # Handle UniversalSkillOutput format (legacy)
        elif isinstance(result, UniversalSkillOutput):
            result_dict = result.model_dump()
            return LearningResponse(result=result_dict)
        # Handle legacy format
        elif hasattr(result, "model_dump"):
            return LearningResponse(result=result.model_dump())
        else:
            return LearningResponse(result={"raw": str(result)})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learning roadmap generation failed: {str(e)}")
