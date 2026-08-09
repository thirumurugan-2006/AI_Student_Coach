from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

class ReflectionRequest(BaseModel):
    reflection_response: str

class ReflectionResponse(BaseModel):
    result: Dict[str, Any]

@router.post("/", response_model=ReflectionResponse)
async def conduct_reflection(
    request: Request, 
    payload: ReflectionRequest,
    user_id: str
):
    """
    Endpoint for conducting reflection sessions to measure confidence and capture learning insights.
    """
    try:
        career_agent = getattr(request.app.state, 'career_agent', None)
        if not career_agent:
            raise HTTPException(
                status_code=503, 
                detail="AI features not available. GROQ_API_KEY is not configured. Please configure the API key in backend/.env"
            )
        
        context = {
            "reflection_response": payload.reflection_response
        }
        
        result = await career_agent.handle_request(
            student_id=user_id,
            skill_name="reflection",
            context=context
        )
        
        return ReflectionResponse(
            result=result.model_dump() if hasattr(result, "model_dump") else result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reflection execution failed: {str(e)}")
