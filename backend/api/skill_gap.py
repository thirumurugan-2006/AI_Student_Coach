from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
from skills.skill_gap.schema import SkillGapOutput
from core.logger import logger

router = APIRouter()


class SkillGapRequest(BaseModel):
    pass  # No input needed, uses student memory


class SkillGapResponse(BaseModel):
    skill_gaps: list
    strengths: list
    weaknesses: list
    readiness_score: float
    recommendations: list
    next_action: str


@router.post("/", response_model=SkillGapResponse)
async def analyze_skill_gap(
    request: Request,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    Analyze skill gaps based on assessment results.
    
    Uses the Skill Gap skill to identify areas for improvement.
    """
    try:
        logger.info(f"Skill gap analysis request for user {user_id}")
        
        # Check if career agent is initialized
        career_agent = getattr(request.app.state, 'career_agent', None)
        if not career_agent:
            raise HTTPException(
                status_code=503,
                detail="AI features not available. GROQ_API_KEY is not configured."
            )
        
        context = {}
        
        # Execute the skill gap skill via orchestrator
        result = await career_agent.handle_request(
            student_id=user_id,
            skill_name="skill_gap",
            context=context,
            schema=SkillGapOutput
        )
        
        # Handle structured output
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return SkillGapResponse(
                skill_gaps=result_dict.get('gaps', []),
                strengths=result_dict.get('strengths', []),
                weaknesses=result_dict.get('weaknesses', []),
                readiness_score=result_dict.get('readiness', 0.0),
                recommendations=result_dict.get('recommendations', []),
                next_action=result_dict.get('next_action', 'roadmap')
            )
        else:
            raise HTTPException(status_code=500, detail="Invalid skill gap output format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Skill gap analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Skill gap analysis failed: {str(e)}")
