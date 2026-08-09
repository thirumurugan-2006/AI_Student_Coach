from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
from skills.roadmap.schema import RoadmapOutput
from core.logger import logger

router = APIRouter()


class RoadmapRequest(BaseModel):
    topic_request: str


class RoadmapResponse(BaseModel):
    roadmap: list
    timeline: str
    milestones: list
    recommendations: list
    next_action: str


@router.post("/", response_model=RoadmapResponse)
async def generate_roadmap(
    request: Request,
    payload: RoadmapRequest,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    Generate a personalized learning roadmap.
    
    Uses the Roadmap skill to create a learning plan based on skill gaps.
    """
    try:
        logger.info(f"Roadmap generation request for user {user_id}: {payload.topic_request}")
        
        # Check if career agent is initialized
        career_agent = getattr(request.app.state, 'career_agent', None)
        if not career_agent:
            raise HTTPException(
                status_code=503,
                detail="AI features not available. GROQ_API_KEY is not configured."
            )
        
        context = {"topic_request": payload.topic_request}
        
        # Execute the roadmap skill via orchestrator
        result = await career_agent.handle_request(
            student_id=user_id,
            skill_name="roadmap",
            context=context,
            schema=RoadmapOutput
        )
        
        # Handle structured output
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return RoadmapResponse(
                roadmap=result_dict.get('topics', []),
                timeline=result_dict.get('timeline', ''),
                milestones=result_dict.get('milestones', []),
                recommendations=result_dict.get('recommendations', []),
                next_action=result_dict.get('next_action', 'learning')
            )
        else:
            raise HTTPException(status_code=500, detail="Invalid roadmap output format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Roadmap generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Roadmap generation failed: {str(e)}")
