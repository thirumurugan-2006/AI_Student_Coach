"""
Career Coach API Endpoints.

Provides a unified conversational endpoint to interact with the
Career Coach orchestrator directly.  Useful for frontend chat UIs.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

from core.dependencies import get_career_agent, get_current_student_id
from core.constants import ALL_SKILLS
from core.logger import api_logger

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class CoachChatRequest(BaseModel):
    """Request payload for a generic career coach interaction."""
    skill: str = Field(
        ...,
        description=f"The skill to invoke. One of: {ALL_SKILLS}",
        examples=["survey"]
    )
    message: str = Field(
        ...,
        description="The user's message or input for the skill",
        min_length=1,
        max_length=4096
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context key-value pairs passed to the skill"
    )


class CoachChatResponse(BaseModel):
    """Response from the Career Coach."""
    skill: str
    student_id: str
    result: Any
    success: bool = True
    message: str = "Request processed successfully"


class CoachStatusResponse(BaseModel):
    """Status of registered skills in the Career Coach."""
    registered_skills: list[str]
    total_skills: int
    agent_ready: bool


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=CoachChatResponse, summary="Interact with Career Coach")
async def coach_chat(
    payload: CoachChatRequest,
    student_id: str = Depends(get_current_student_id),
    career_agent=Depends(get_career_agent),
):
    """
    Generic conversational endpoint for the Career Coach.

    Routes the request to the correct skill via the Career Coach orchestrator.
    The orchestrator handles memory, evaluation, and response formatting.
    """
    if payload.skill not in ALL_SKILLS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown skill '{payload.skill}'. Valid skills: {ALL_SKILLS}"
        )

    api_logger.info(
        f"Coach chat — student={student_id}, skill={payload.skill}"
    )

    # Merge explicit context with the user message
    context: Dict[str, Any] = payload.context or {}
    context["current_message"] = payload.message

    try:
        result = await career_agent.handle_request(
            student_id=student_id,
            skill_name=payload.skill,
            context=context,
        )

        # Serialise Pydantic models to dict for consistent JSON output
        serialised = (
            result.model_dump()
            if hasattr(result, "model_dump")
            else result
        )

        return CoachChatResponse(
            skill=payload.skill,
            student_id=student_id,
            result=serialised,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        api_logger.error(f"Coach chat failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Career Coach request failed: {str(e)}"
        )


@router.get("/status", response_model=CoachStatusResponse, summary="Career Coach status")
async def coach_status(career_agent=Depends(get_career_agent)):
    """
    Return the list of registered skills and agent readiness status.
    """
    registered = list(career_agent.registry._skills.keys())
    return CoachStatusResponse(
        registered_skills=registered,
        total_skills=len(registered),
        agent_ready=True,
    )


@router.get("/skills", summary="List available skills")
async def list_skills():
    """Return all skill names the Career Coach supports."""
    return {"skills": ALL_SKILLS, "count": len(ALL_SKILLS)}
