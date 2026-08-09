from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any
from pipelines.pipeline_result import PipelineResult
from core.skill_output import UniversalSkillOutput
from core.logger import logger

router = APIRouter()

class InterviewRequest(BaseModel):
    company_name: str
    job_role: str
    user_response: str

class InterviewResponse(BaseModel):
    result: Dict[str, Any]

@router.post("/", response_model=InterviewResponse)
async def conduct_interview(
    request: Request,
    payload: InterviewRequest,
    user_id: str = Query(..., description="The student's user ID returned from /user/signup"),
):
    """
    Endpoint for simulating real recruiter interviews.
    """
    try:
        career_agent = getattr(request.app.state, 'career_agent', None)
        if not career_agent:
            raise HTTPException(
                status_code=503, 
                detail="AI features not available. GROQ_API_KEY is not configured. Please configure the API key in backend/.env"
            )
        
        context = {
            "company": payload.company_name,
            "role": payload.job_role,
            "current_answer": payload.user_response
        }
        
        result = await career_agent.handle_request(
            student_id=user_id,
            skill_name="interview",
            context=context
        )
        
        # Ensure result is not a coroutine
        if hasattr(result, '__await__'):
            logger.error("Result is a coroutine, awaiting it...")
            result = await result
        
        # Handle PipelineResult format (new pipeline architecture)
        if isinstance(result, PipelineResult):
            result_dict = result.model_dump()
            return InterviewResponse(result=result_dict)
        # Handle UniversalSkillOutput format (legacy)
        elif isinstance(result, UniversalSkillOutput):
            result_dict = result.model_dump()
            return InterviewResponse(result=result_dict)
        # Handle legacy format
        elif hasattr(result, "model_dump"):
            return InterviewResponse(result=result.model_dump())
        else:
            return InterviewResponse(result={"raw": str(result)})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview execution failed: {str(e)}")
