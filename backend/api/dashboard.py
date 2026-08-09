from fastapi import APIRouter, Request, HTTPException, Depends
from auth.dependencies import get_current_student_id
from services.recommendation_service import RecommendationService
from core.helpers import normalize_text, safe_get

router = APIRouter()

@router.get("/")
async def get_dashboard(
    request: Request, 
    student_id: str = Depends(get_current_student_id)
):
    """
    Endpoint for retrieving a student's full dashboard and progress.
    Integrates Recommendation Engine for next actions and priorities.
    Returns safe defaults for missing data to prevent NoneType errors.
    """
    try:
        memory = request.app.state.memory
        profile = memory.get_profile(student_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Generate recommendations using Recommendation Engine
        recommendation_service = RecommendationService(memory=memory)
        recommendations = recommendation_service.get_recommendations(student_id)
            
        # Safely extract all fields with defaults to prevent NoneType errors
        return {
            "student_id": safe_get(profile, "id", ""),
            "name": safe_get(profile, "name", ""),
            "career_goal": safe_get(profile, "career_goal"),
            "target_role": safe_get(profile, "target_role"),
            "readiness_score": safe_get(profile, "readiness_score", 0),
            "completed_topics": safe_get(profile, "completed_topics", []),
            "roadmap": safe_get(profile, "roadmap", []),
            "assessment_history": safe_get(profile, "assessment_history", []),
            "interview_history": safe_get(profile, "interview_history", []),
            "reflection_notes": safe_get(profile, "reflection_notes", []),
            "skills": safe_get(profile, "skills", {}),
            "skill_gaps": safe_get(profile, "skill_gaps", []),
            "learning_progress": safe_get(profile, "learning_progress", 0),
            "placement_score": safe_get(profile, "placement_score"),
            "recommendations": recommendations
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard retrieval failed: {str(e)}")
