"""
Placement API Endpoints

Provides REST API endpoints for placement preparation functionality.
"""

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from skills.placement.schema import PlacementOutput
from core.logger import logger

router = APIRouter()


class PlacementAssessmentRequest(BaseModel):
    """Request model for placement assessment."""
    target_role: Optional[str] = None
    target_companies: Optional[List[str]] = None


class PlacementAssessmentResponse(BaseModel):
    """Response model for placement assessment."""
    status: str
    profile: Dict[str, Any]
    recommendations: List[str]
    next_steps: List[str]
    estimated_timeline: str
    confidence: float
    message: str


class PlacementProgressResponse(BaseModel):
    """Response model for placement progress."""
    student_id: str
    career_goal: Optional[str]
    target_company: Optional[str]
    readiness_score: float
    completed_topics: List[str]
    roadmap: List[str]


@router.post("/assess", response_model=PlacementAssessmentResponse)
async def assess_placement_readiness(
    request: Request,
    payload: PlacementAssessmentRequest,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    Assess student's placement readiness.
    
    Evaluates technical skills, communication, interview preparation, and resume quality.
    Provides actionable recommendations and next steps.
    """
    try:
        logger.info(f"Placement assessment request for user {user_id}")
        
        # Check if placement simulator is initialized
        placement_simulator = getattr(request.app.state, 'placement_simulator', None)
        if not placement_simulator:
            raise HTTPException(
                status_code=503, 
                detail="AI features not available. GROQ_API_KEY is not configured. Please configure the API key in backend/.env"
            )
        
        # Perform placement assessment
        result = await placement_simulator.assess_placement_readiness(
            student_id=user_id,
            target_role=payload.target_role,
            target_companies=payload.target_companies
        )
        
        # Convert to response format
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
        else:
            result_dict = {"raw_result": str(result)}
        
        return PlacementAssessmentResponse(
            status=result_dict.get('status', 'unknown'),
            profile=result_dict.get('profile', {}),
            recommendations=result_dict.get('recommendations', []),
            next_steps=result_dict.get('next_steps', []),
            estimated_timeline=result_dict.get('estimated_timeline', 'Unknown'),
            confidence=result_dict.get('confidence', 0.0),
            message=f"Placement assessment completed. Status: {result_dict.get('status', 'unknown')}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Placement assessment error: {e}")
        raise HTTPException(status_code=500, detail=f"Placement assessment failed: {str(e)}")


@router.get("/progress", response_model=PlacementProgressResponse)
async def get_placement_progress(
    request: Request,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    Get student's placement progress summary.
    
    Returns current placement readiness status and progress.
    """
    try:
        logger.info(f"Placement progress request for user {user_id}")
        
        # Check if placement simulator is initialized
        placement_simulator = getattr(request.app.state, 'placement_simulator', None)
        if not placement_simulator:
            raise HTTPException(
                status_code=503, 
                detail="AI features not available. GROQ_API_KEY is not configured. Please configure the API key in backend/.env"
            )
        
        # Get placement progress
        progress = await placement_simulator.get_placement_progress(user_id)
        
        if "error" in progress:
            raise HTTPException(status_code=404, detail=progress["error"])
        
        return PlacementProgressResponse(
            student_id=progress.get("student_id", user_id),
            career_goal=progress.get("career_goal"),
            target_company=progress.get("target_company"),
            readiness_score=progress.get("readiness_score", 0.0),
            completed_topics=progress.get("completed_topics", []),
            roadmap=progress.get("roadmap", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Placement progress error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get placement progress: {str(e)}")
