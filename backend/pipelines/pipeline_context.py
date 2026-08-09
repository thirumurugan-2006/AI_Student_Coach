"""
PipelineContext

Controlled state object for Pipeline execution.
Provides a consistent context structure across all pipelines.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class PipelineContext(BaseModel):
    """Context object for Pipeline execution."""
    
    student_id: str = Field(
        description="Student's unique identifier"
    )
    current_module: str = Field(
        default="preparation",
        description="Current module: preparation or placement"
    )
    current_skill: str = Field(
        description="Current skill being executed"
    )
    workflow_state: str = Field(
        default="signup",
        description="Current workflow state"
    )
    student_memory: Dict[str, Any] = Field(
        default_factory=dict,
        description="Student's current memory/profile"
    )
    career_intelligence: Dict[str, Any] = Field(
        default_factory=dict,
        description="Career intelligence data"
    )
    target_role: Optional[str] = Field(
        default=None,
        description="Student's target career role"
    )
    skill_gaps: List[str] = Field(
        default_factory=list,
        description="Current skill gaps"
    )
    question_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Previous questions asked to this student"
    )
    previous_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Result from the previous pipeline execution"
    )
    additional_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context specific to the current pipeline"
    )
