"""
Technical Skill Output Schema
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class TechnicalQuestion(BaseModel):
    question: str = Field(..., description="The technical question")
    topic: str = Field(..., description="Topic: python, sql, system_design, etc.")
    difficulty: str = Field(..., description="Difficulty: easy, medium, hard")


class TechnicalOutput(BaseModel):
    question: TechnicalQuestion
    is_complete: bool = Field(False, description="True if the technical round is finished")
