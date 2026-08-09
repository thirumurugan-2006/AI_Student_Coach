"""
HR Skill Output Schema
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class HRQuestion(BaseModel):
    question: str = Field(..., description="The HR question")
    category: str = Field(..., description="Category: behavioral, cultural_fit, situational")


class HROutput(BaseModel):
    question: HRQuestion
    is_complete: bool = Field(False, description="True if the HR round is finished")
