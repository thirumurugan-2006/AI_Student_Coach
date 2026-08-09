from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
from skills.survey.schema import SurveyOutput
from core.skill_output import UniversalSkillOutput
from pipelines.pipeline_result import PipelineResult
from core.logger import logger

router = APIRouter()

class SurveyRequest(BaseModel):
    user_message: str
    question_id: Optional[str] = None

class SurveyResponse(BaseModel):
    response_message: str
    profile_updated: bool
    survey_completed: bool
    mcq_question: Optional[Dict[str, Any]] = None
    next_action: Optional[str] = None
    next_action_reason: Optional[str] = None
    error_message: Optional[str] = None

@router.post("/", response_model=SurveyResponse)
async def conduct_survey(
    request: Request,
    payload: SurveyRequest,
    user_id: str = Query(..., description="The student's user ID returned from /user/signup"),
):
    """
    Endpoint for conducting the AI Career Discovery Survey.
    Interacts with the Career Coach orchestrator to process the survey skill.
    """
    print(f"=== SURVEY API ENTRY POINT ===")
    print(f"Survey request received for user {user_id}: {payload.user_message}")
    logger.info(f"=== SURVEY API ENTRY POINT ===")
    logger.info(f"Survey request received for user {user_id}: {payload.user_message}")
    
    try:
        logger.info(f"=== SURVEY API START ===")
        logger.info(f"Survey request received for user {user_id}: {payload.user_message}")
        
        # Check if career agent is initialized
        career_agent = getattr(request.app.state, 'career_agent', None)
        if not career_agent:
            logger.error("Career agent not initialized")
            raise HTTPException(
                status_code=503, 
                detail="AI features not available. GROQ_API_KEY is not configured. Please configure the API key in backend/.env"
            )
        
        logger.info(f"Career agent found: {type(career_agent)}")
        
        # Route to answer pipeline when question_id is provided
        skill_name = "survey_answer" if payload.question_id else "survey"
        context = {
            "current_message": payload.user_message,
            "question_id": payload.question_id,
            "user_answer": payload.user_message if payload.question_id else None,
        }
        
        logger.info(f"Context built: {context}")
        logger.info(f"Calling career_agent.handle_request with skill_name='{skill_name}'")
        
        # Execute the survey skill via orchestrator with proper schema
        result = await career_agent.handle_request(
            student_id=user_id,
            skill_name=skill_name,
            context=context,
            schema=SurveyOutput
        )
        
        logger.info(f"Result received from career_agent.handle_request: {type(result)}")
        
        # Ensure result is not a coroutine
        if hasattr(result, '__await__'):
            logger.error("Result is a coroutine, awaiting it...")
            result = await result
            logger.info(f"After await, result type: {type(result)}")
        
        # Handle PipelineResult format (new pipeline architecture)
        if isinstance(result, PipelineResult):
            result_dict = result.model_dump()
            response_message = result_dict.get('result', {}).get('response_message') or result_dict.get('result', {}).get('coach_notification') or f"Survey status: {result_dict.get('status')}"
            survey_completed = result_dict.get('result', {}).get('survey_completed', False)
            mcq_question = result_dict.get('result', {}).get('mcq_question')
            next_action = result_dict.get('next_action')
            next_action_reason = result_dict.get('next_action_reason')
            error_message = result_dict.get('error_message')
        # Handle universal output format (legacy)
        elif isinstance(result, UniversalSkillOutput):
            result_dict = result.model_dump()
            response_message = result_dict.get('result', {}).get('coach_notification') or f"Survey status: {result_dict.get('status')}"
            survey_completed = result_dict.get('result', {}).get('survey_completed', False)
            mcq_question = result_dict.get('result', {}).get('mcq_question')
            next_action = result_dict.get('next_action')
            next_action_reason = result_dict.get('next_action_reason')
        # Handle legacy format
        elif hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            response_message = result_dict.get('coach_notification') or f"Survey status: {result_dict.get('status')}"
            survey_completed = result_dict.get('survey_completed', False)
            mcq_question = result_dict.get('mcq_question')
            next_action = "assessment" if survey_completed else "survey"
            next_action_reason = "Survey completed, moving to assessment" if survey_completed else "Continue survey"
            # Convert mcquestion to dict if it's a Pydantic model
            if mcq_question and hasattr(mcq_question, 'model_dump'):
                mcq_question = mcq_question.model_dump()
        else:
            response_message = str(result)
            survey_completed = False
            mcq_question = None
            next_action = "survey"
            next_action_reason = "Continue survey"
        
        return SurveyResponse(
            response_message=response_message,
            profile_updated=True,
            survey_completed=survey_completed,
            mcq_question=mcq_question,
            next_action=next_action,
            next_action_reason=next_action_reason
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Survey error: {e}")
        raise HTTPException(status_code=500, detail=f"Survey execution failed: {str(e)}")
