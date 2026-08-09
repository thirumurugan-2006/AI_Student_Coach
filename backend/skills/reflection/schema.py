from pydantic import BaseModel, Field

class ReflectionOutputSchema(BaseModel):
    """
    Structured output expected from the LLM for the Reflection Skill.
    """
    confidence_level: str = Field(..., description="The user's self-reported confidence level (low, medium, high).")
    reflection_notes: str = Field(..., description="Summary of the user's reflection on their progress.")
    suggested_action: str = Field(..., description="Actionable next step based on the reflection (e.g., review topic X, rest).")
