from pydantic import BaseModel, Field
from typing import List, Dict

class LearningOutputSchema(BaseModel):
    """
    Structured output expected from the LLM for the Learning Skill.
    """
    recommended_resources: List[Dict[str, str]] = Field(..., description="List of learning resources (title, url, type).")
    suggested_projects: List[str] = Field(..., description="Project ideas to practice the concepts.")
    updated_roadmap: List[str] = Field(..., description="The next ordered set of topics to study.")
    study_schedule: str = Field(..., description="A short textual advice on how to structure their study hours.")
