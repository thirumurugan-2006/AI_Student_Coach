"""
Placement Report Schema
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RoundScore(BaseModel):
    round_type: str
    score: float
    feedback: str


class PlacementReport(BaseModel):
    student_id: str
    overall_score: float
    round_scores: List[RoundScore]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    next_best_action: str
    readiness_update: float
