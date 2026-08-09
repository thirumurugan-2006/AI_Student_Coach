from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any
from core.logger import logger

router = APIRouter()


class CareerIntelligenceResponse(BaseModel):
    profile: Dict[str, Any]
    skills: Dict[str, Any]
    skill_gaps: list
    learning_progress: Dict[str, Any]
    assessment_performance: Dict[str, Any]
    placement_performance: Dict[str, Any]
    confidence: float
    readiness: float
    recommendations: list
    next_best_action: str


@router.get("/", response_model=CareerIntelligenceResponse)
async def get_career_intelligence(
    request: Request,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    Get career intelligence data aggregated from student memory and evidence.
    """
    try:
        logger.info(f"Career intelligence request for user {user_id}")

        career_agent = getattr(request.app.state, 'career_agent', None)
        memory = getattr(request.app.state, 'memory', None)
        if not career_agent:
            raise HTTPException(
                status_code=503,
                detail="AI features not available. GROQ_API_KEY is not configured."
            )

        profile = memory.get_profile(user_id) if memory else None
        intel = career_agent.career_intelligence.get_student_intelligence(user_id)

        skills = profile.get("skills", {}) if profile else intel.get("skills", {})
        skill_gaps = profile.get("weak_topics", []) if profile else intel.get("skill_gaps", [])
        readiness_score = profile.get("readiness_score", 0) if profile else 0

        assessment_history = profile.get("assessment_history", []) if profile else []
        avg_score = 0.0
        if assessment_history:
            scores = [a.get("score", 0) for a in assessment_history if isinstance(a, dict)]
            avg_score = sum(scores) / len(scores) if scores else 0.0

        placement_history = profile.get("placement_history", []) if profile else []
        placement_score = 0.0
        if placement_history:
            scores = [p.get("score", 0) for p in placement_history if isinstance(p, dict)]
            placement_score = sum(scores) / len(scores) if scores else 0.0

        recommendations = intel.get("recommendations", [])
        if skill_gaps and not recommendations:
            recommendations = [f"Focus on improving {gap}" for gap in skill_gaps[:3]]

        next_action = career_agent.career_intelligence.calculate_next_best_action(
            student_id=user_id,
            current_stage=profile.get("current_stage", "survey") if profile else "survey",
            readiness_status="ready" if readiness_score >= 70 else "progressing",
            skill_gaps=skill_gaps,
            learning_progress=len(profile.get("completed_topics", [])) if profile else 0,
        )

        return CareerIntelligenceResponse(
            profile={
                "career_goal": profile.get("career_goal") if profile else intel.get("profile", {}).get("career_goal"),
                "target_role": profile.get("career_goal") if profile else None,
                "experience_level": profile.get("experience_level") if profile else None,
                "learning_style": profile.get("learning_style") if profile else None,
            },
            skills=skills,
            skill_gaps=skill_gaps,
            learning_progress={
                "completed_topics": len(profile.get("completed_topics", [])) if profile else 0,
                "total_topics": len(profile.get("roadmap", [])) if profile else 0,
                "current_topic": profile.get("roadmap", [None])[0] if profile and profile.get("roadmap") else None,
            },
            assessment_performance={
                "average_score": avg_score,
                "total_assessments": len(assessment_history),
            },
            placement_performance={
                "overall_score": placement_score,
                "rounds_completed": len(placement_history),
            },
            confidence=min(readiness_score / 100.0, 1.0) if readiness_score else 0.5,
            readiness=readiness_score / 100.0 if readiness_score else 0.0,
            recommendations=recommendations,
            next_best_action=next_action,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Career intelligence error: {e}")
        raise HTTPException(status_code=500, detail=f"Career intelligence retrieval failed: {str(e)}")
