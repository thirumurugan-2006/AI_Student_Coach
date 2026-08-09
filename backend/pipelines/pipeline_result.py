"""
PipelineResult

Standard result structure for all Pipeline executions.
Every Pipeline must return a PipelineResult for consistent API responses.
"""

from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field


class PipelineResult(BaseModel):
    """Standard result structure for all Pipeline executions."""
    
    status: Literal["success", "failed", "in_progress"] = Field(
        description="Status of the pipeline execution"
    )
    pipeline: str = Field(
        description="Name of the pipeline that was executed"
    )
    skill: str = Field(
        description="Name of the skill that was executed"
    )
    current_module: Literal["preparation", "placement"] = Field(
        description="Current module: preparation or placement"
    )
    result: Dict[str, Any] = Field(
        default_factory=dict,
        description="The actual result from the skill (question, learning plan, etc.)"
    )
    evaluation: Dict[str, Any] = Field(
        default_factory=dict,
        description="Evaluation metrics (scores, strengths, weaknesses)"
    )
    evidence: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Evidence collected for career intelligence"
    )
    progress: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Progress through the current module (0.0 to 1.0)"
    )
    next_action: str = Field(
        description="Next action to take in the workflow"
    )
    next_action_reason: str = Field(
        description="Reason for the recommended next action"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if status is 'failed'"
    )
