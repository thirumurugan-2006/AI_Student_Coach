from pydantic import BaseModel, Field
from typing import Dict, Any

class InterviewOutputSchema(BaseModel):
    """
    Structured output expected from the LLM for the Interview Skill.
    """
    next_question: str = Field(..., description="The next recruiter question based on the user's resume or project.")
    feedback: Dict[str, Any] = Field(..., description="Recruiter feedback on the previous answer, noting strengths and areas for improvement.")
    overall_score: int = Field(0, description="Score from 0-100 on the user's interview performance so far.")
    is_complete: bool = Field(False, description="True if the simulated interview session is finished.")
