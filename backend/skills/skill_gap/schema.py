"""
Skill Gap Skill Schema

Defines the structured output for identifying skill gaps based on assessment results.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SkillGapAnalysis(BaseModel):
    """Analysis of a specific skill gap."""
    
    skill: str = Field(..., description="The skill with a gap")
    current_level: str = Field(..., description="Current mastery level: needs_improvement, learning, mastered")
    target_level: str = Field(..., description="Target mastery level for the career goal")
    gap_severity: str = Field(..., description="Severity of the gap: critical, moderate, minor")
    recommended_resources: List[str] = Field(
        default_factory=list,
        description="Recommended learning resources"
    )
    estimated_time: str = Field(..., description="Estimated time to close the gap")


class SkillGapOutput(BaseModel):
    """Skill Gap skill output schema."""
    
    status: str = Field(description="Analysis status: completed, in_progress")
    
    skill_gaps: List[SkillGapAnalysis] = Field(
        default_factory=list,
        description="List of identified skill gaps"
    )
    
    strengths: List[str] = Field(
        default_factory=list,
        description="Student's current strengths"
    )
    
    priority_gaps: List[str] = Field(
        default_factory=list,
        description="Gaps that should be addressed first"
    )
    
    overall_readiness: float = Field(
        ge=0,
        le=100,
        description="Overall skill readiness percentage"
    )
    
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations for addressing gaps"
    )
    
    next_action: str = Field(description="Recommended next action: roadmap, learning")
