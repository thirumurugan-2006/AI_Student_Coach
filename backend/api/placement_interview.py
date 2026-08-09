from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
from skills.placement_interview.schema import InterviewOutput
from core.logger import logger

router = APIRouter()


class InterviewRequest(BaseModel):
    pass  # No input needed, uses student memory


class InterviewResponse(BaseModel):
    question: Dict[str, Any]
    score: Optional[float] = None
    strengths: Optional[list] = None
    weaknesses: Optional[list] = None
    next_action: str


@router.post("/", response_model=InterviewResponse)
async def conduct_interview_round(
    request: Request,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    Conduct placement interview round.
    
    Uses the Placement Interview skill to generate behavioral and situational interview questions.
    """
    try:
        logger.info(f"Placement interview round request for user {user_id}")
        
        # Check if career agent is initialized
        career_agent = getattr(request.app.state, 'career_agent', None)
        if not career_agent:
            raise HTTPException(
                status_code=503,
                detail="AI features not available. GROQ_API_KEY is not configured."
            )
        
        context = {}
        
        # Execute the placement interview skill via orchestrator
        result = await career_agent.handle_request(
            student_id=user_id,
            skill_name="placement_interview",
            context=context,
            schema=InterviewOutput
        )
        
        # Handle structured output
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return InterviewResponse(
                question=result_dict.get('question', {}),
                score=result_dict.get('score'),
                strengths=result_dict.get('strengths'),
                weaknesses=result_dict.get('weaknesses'),
                next_action=result_dict.get('next_action', 'placement_hr')
            )
        else:
            raise HTTPException(status_code=500, detail="Invalid interview output format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Placement interview round error: {e}")
        raise HTTPException(status_code=500, detail=f"Placement interview round failed: {str(e)}")
