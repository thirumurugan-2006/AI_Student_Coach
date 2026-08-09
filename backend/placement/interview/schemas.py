"""
Interview Skill Output Schema
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    question: str = Field(..., description="The interview question")
    category: str = Field(..., description="Category: technical, behavioral, situational")


class InterviewOutput(BaseModel):
    question: InterviewQuestion
    is_complete: bool = Field(False, description="True if the interview round is finished")
