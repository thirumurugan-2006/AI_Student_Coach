"""
Universal Skill Output Contract

All skills must return this common wrapper structure to ensure
consistent API responses and workflow integration.
"""

from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field


class UniversalSkillOutput(BaseModel):
    """
    Universal output contract for all skills.
    
    Every skill must return this structure to ensure:
    - Consistent API responses
    - Proper workflow integration
    - Clear next_action routing
    - Evidence collection
    - Progress tracking
    """
    
    status: Literal["in_progress", "completed", "failed"] = Field(
        description="Status of the skill execution"
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
