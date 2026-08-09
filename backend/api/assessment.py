from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
from pipelines.pipeline_result import PipelineResult
from core.skill_output import UniversalSkillOutput
from core.logger import logger

router = APIRouter()

class AssessmentRequest(BaseModel):
    topic: str
    answer: Optional[str] = None
    question_id: Optional[str] = None

class AssessmentResponse(BaseModel):
    result: Dict[str, Any]

@router.post("/", response_model=AssessmentResponse)
async def conduct_assessment(
    request: Request,
    payload: AssessmentRequest,
    user_id: str = Query(..., description="The student's user ID returned from /user/signup"),
):
    """
    Endpoint for generating and evaluating adaptive assessments.
    """
    try:
        career_agent = getattr(request.app.state, 'career_agent', None)
        if not career_agent:
            raise HTTPException(
                status_code=503, 
                detail="AI features not available. GROQ_API_KEY is not configured. Please configure the API key in backend/.env"
            )
        
        skill_name = "assessment_answer" if payload.question_id and payload.answer else "assessment"
        context = {
            "topic": payload.topic,
            "answer": payload.answer,
            "question_id": payload.question_id,
            "user_answer": payload.answer,
        }
        
        result = await career_agent.handle_request(
            student_id=user_id,
            skill_name=skill_name,
            context=context
        )
        
        # Ensure result is not a coroutine
        if hasattr(result, '__await__'):
            logger.error("Result is a coroutine, awaiting it...")
            result = await result
        
        # Handle PipelineResult format (new pipeline architecture)
        if isinstance(result, PipelineResult):
            result_dict = result.model_dump()
            return AssessmentResponse(result=result_dict)
        # Handle UniversalSkillOutput format (legacy)
        elif isinstance(result, UniversalSkillOutput):
            result_dict = result.model_dump()
            return AssessmentResponse(result=result_dict)
        # Handle legacy format
        elif hasattr(result, "model_dump"):
            return AssessmentResponse(result=result.model_dump())
        else:
            return AssessmentResponse(result={"raw": str(result)})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment execution failed: {str(e)}")
