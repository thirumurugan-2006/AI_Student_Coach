from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
from skills.placement_aptitude.schema import AptitudeOutput
from core.logger import logger

router = APIRouter()


class AptitudeRequest(BaseModel):
    pass  # No input needed, uses student memory


class AptitudeResponse(BaseModel):
    question: Dict[str, Any]
    score: Optional[float] = None
    strengths: Optional[list] = None
    weaknesses: Optional[list] = None
    next_action: str


@router.post("/", response_model=AptitudeResponse)
async def conduct_aptitude_round(
    request: Request,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    Conduct placement aptitude round.
    
    Uses the Placement Aptitude skill to generate quantitative, logical, and verbal reasoning questions.
    """
    try:
        logger.info(f"Placement aptitude round request for user {user_id}")
        
        # Check if career agent is initialized
        career_agent = getattr(request.app.state, 'career_agent', None)
        if not career_agent:
            raise HTTPException(
                status_code=503,
                detail="AI features not available. GROQ_API_KEY is not configured."
            )
        
        context = {}
        
        # Execute the placement aptitude skill via orchestrator
        result = await career_agent.handle_request(
            student_id=user_id,
            skill_name="placement_aptitude",
            context=context,
            schema=AptitudeOutput
        )
        
        # Handle structured output
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return AptitudeResponse(
                question=result_dict.get('question', {}),
                score=result_dict.get('score'),
                strengths=result_dict.get('strengths'),
                weaknesses=result_dict.get('weaknesses'),
                next_action=result_dict.get('next_action', 'placement_coding')
            )
        else:
            raise HTTPException(status_code=500, detail="Invalid aptitude output format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Placement aptitude round error: {e}")
        raise HTTPException(status_code=500, detail=f"Placement aptitude round failed: {str(e)}")
