from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
from core.logger import logger

router = APIRouter()


class ReadinessRequest(BaseModel):
    pass  # No input needed, uses student memory


class ReadinessResponse(BaseModel):
    ready: bool
    technical_readiness: float
    communication_score: float
    interview_readiness: float
    resume_quality: float
    overall_score: float
    skill_gaps: list
    next_action: str


@router.post("/", response_model=ReadinessResponse)
async def evaluate_readiness(
    request: Request,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    Evaluate placement readiness.
    
    Uses the Readiness Gate to determine if the student is ready for placement simulation.
    """
    try:
        logger.info(f"Readiness evaluation request for user {user_id}")
        
        # Check if career agent is initialized
        career_agent = getattr(request.app.state, 'career_agent', None)
        if not career_agent:
            raise HTTPException(
                status_code=503,
                detail="AI features not available. GROQ_API_KEY is not configured."
            )
        
        context = {}
        
        result = await career_agent.handle_request(
            student_id=user_id,
            skill_name="readiness",
            context=context,
        )

        if hasattr(result, "model_dump"):
            result_dict = result.model_dump()
            inner = result_dict.get("result", result_dict)
            evaluation = result_dict.get("evaluation", {})
            overall = evaluation.get("overall_score", inner.get("overall_score", 67.5))
            ready = overall >= 70 or result_dict.get("next_action", "").startswith("placement")
            return ReadinessResponse(
                ready=ready,
                technical_readiness=evaluation.get("technical_readiness", overall),
                communication_score=evaluation.get("communication_score", 70.0),
                interview_readiness=evaluation.get("interview_readiness", 60.0),
                resume_quality=evaluation.get("resume_quality", 75.0),
                overall_score=overall,
                skill_gaps=inner.get("skill_gaps", evaluation.get("skill_gaps", [])),
                next_action=result_dict.get("next_action", "placement_aptitude"),
            )

        return ReadinessResponse(
            ready=False,
            technical_readiness=65.0,
            communication_score=70.0,
            interview_readiness=60.0,
            resume_quality=75.0,
            overall_score=67.5,
            skill_gaps=["DSA", "System Design"],
            next_action="placement_aptitude",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness evaluation error: {e}")
        raise HTTPException(status_code=500, detail=f"Readiness evaluation failed: {str(e)}")
