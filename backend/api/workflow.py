from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
from core.workflow_controller import WorkflowController, WorkflowState, Skill
from core.logger import logger

router = APIRouter()


class WorkflowStateResponse(BaseModel):
    current_module: str
    current_skill: str
    next_action: Optional[str]
    progress: float
    status: str
    next_action_reason: Optional[str]


class SkillResultRequest(BaseModel):
    user_id: str
    skill: str
    result: Dict[str, Any]


class SkillResultResponse(BaseModel):
    evaluation: Dict[str, Any]
    next_action: str
    next_action_reason: str
    progress: float


@router.get("/state", response_model=WorkflowStateResponse)
async def get_workflow_state(
    request: Request,
    user_id: str = Query(..., description="The student's user ID"),
):
    """
    Get current workflow state from the Workflow Controller.
    
    Returns the current module, skill, next action, progress, and status.
    """
    try:
        logger.info(f"Workflow state request for user {user_id}")
        
        # Get workflow controller from app state
        workflow_controller = getattr(request.app.state, 'workflow_controller', None)
        if not workflow_controller:
            # Initialize if not exists
            workflow_controller = WorkflowController()
            request.app.state.workflow_controller = workflow_controller
        
        # Get current state for user (simplified - in production, would fetch from database)
        # For now, return a default state
        return WorkflowStateResponse(
            current_module="career_preparation",
            current_skill="survey",
            next_action="survey",
            progress=0.0,
            status="in_progress",
            next_action_reason="Starting career discovery survey"
        )
    except Exception as e:
        logger.error(f"Workflow state error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow state: {str(e)}")


@router.post("/state", response_model=SkillResultResponse)
async def submit_skill_result(
    request: Request,
    payload: SkillResultRequest,
):
    """
    Submit skill result to backend for evaluation and next action.
    
    The backend evaluates the result, updates memory, and returns the next action.
    """
    try:
        logger.info(f"Skill result submission for user {payload.user_id}, skill {payload.skill}")
        
        # Get workflow controller from app state
        workflow_controller = getattr(request.app.state, 'workflow_controller', None)
        if not workflow_controller:
            workflow_controller = WorkflowController()
            request.app.state.workflow_controller = workflow_controller
        
        # Get career agent for evaluation
        career_agent = getattr(request.app.state, 'career_agent', None)
        if not career_agent:
            raise HTTPException(
                status_code=503,
                detail="AI features not available. GROQ_API_KEY is not configured."
            )
        
        # Determine next action based on skill and result
        # This is a simplified implementation - in production, would use the Planner
        skill_to_next_action = {
            "survey": "assessment",
            "assessment": "skill_gap",
            "skill_gap": "roadmap",
            "roadmap": "learning",
            "learning": "reflection",
            "reflection": "readiness",
            "readiness": "placement_aptitude",
            "placement_aptitude": "placement_coding",
            "placement_coding": "placement_technical",
            "placement_technical": "placement_interview",
            "placement_interview": "placement_hr",
            "placement_hr": "placement_report",
            "placement_report": "dashboard",
        }
        
        next_action = skill_to_next_action.get(payload.skill, "dashboard")
        
        # Calculate progress based on skill
        skill_progress = {
            "survey": 15,
            "assessment": 30,
            "skill_gap": 40,
            "roadmap": 50,
            "learning": 60,
            "reflection": 70,
            "readiness": 80,
            "placement_aptitude": 85,
            "placement_coding": 90,
            "placement_technical": 93,
            "placement_interview": 96,
            "placement_hr": 98,
            "placement_report": 100,
        }
        
        progress = skill_progress.get(payload.skill, 0)
        
        return SkillResultResponse(
            evaluation=payload.result,
            next_action=next_action,
            next_action_reason=f"Completed {payload.skill}, moving to {next_action}",
            progress=progress
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Skill result submission error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit skill result: {str(e)}")
