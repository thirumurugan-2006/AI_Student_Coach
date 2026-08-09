"""
Coding Skill Output Schema
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CodingProblem(BaseModel):
    title: str = Field(..., description="Problem title")
    description: str = Field(..., description="Problem description")
    difficulty: str = Field(..., description="Difficulty: easy, medium, hard")
    language: str = Field(..., description="Programming language")
    test_cases: List[dict] = Field(..., description="Test cases for evaluation")
    evaluation_criteria: List[str] = Field(..., description="Criteria for evaluation")


class CodingOutput(BaseModel):
    problem: CodingProblem
    is_complete: bool = Field(False, description="True if the coding round is finished")
