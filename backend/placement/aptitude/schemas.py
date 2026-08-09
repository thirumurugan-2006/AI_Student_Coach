"""
Aptitude Skill Output Schema
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AptitudeQuestion(BaseModel):
    question: str = Field(..., description="The aptitude question text")
    options: List[str] = Field(..., description="Multiple choice options")
    correct_answer: str = Field(..., description="The correct option text")
    topic: str = Field(..., description="Topic: logical_reasoning, quantitative, verbal")
    difficulty: str = Field(..., description="Difficulty: easy, medium, hard")


class AptitudeOutput(BaseModel):
    question: AptitudeQuestion
    is_complete: bool = Field(False, description="True if the aptitude round is finished")
