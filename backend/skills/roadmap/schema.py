"""
Roadmap Skill Schema

Defines the structured output for creating personalized learning roadmaps.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class LearningTopic(BaseModel):
    """A specific learning topic in the roadmap."""
    
    topic: str = Field(..., description="The learning topic")
    description: str = Field(..., description="Brief description of what will be learned")
    priority: str = Field(..., description="Priority level: critical, high, medium, low")
    estimated_hours: int = Field(..., description="Estimated hours to complete")
    resources: List[str] = Field(
        default_factory=list,
        description="Recommended learning resources"
    )
    prerequisites: List[str] = Field(
        default_factory=list,
        description="Prerequisite topics"
    )
    success_criteria: List[str] = Field(
        default_factory=list,
        description="Criteria for successful completion"
    )


class RoadmapOutput(BaseModel):
    """Roadmap skill output schema."""
    
    status: str = Field(description="Roadmap status: created, updated")
    
    roadmap: List[LearningTopic] = Field(
        default_factory=list,
        description="Ordered list of learning topics"
    )
    
    total_estimated_hours: int = Field(..., description="Total estimated hours for complete roadmap")
    
    timeline_weeks: int = Field(..., description="Estimated timeline in weeks")
    
    milestones: List[str] = Field(
        default_factory=list,
        description="Key milestones in the learning journey"
    )
    
    recommendations: List[str] = Field(
        default_factory=list,
        description="General recommendations for following the roadmap"
    )
    
    next_action: str = Field(description="Recommended next action: learning")
