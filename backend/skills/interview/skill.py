"""
Interview Skill

Responsible for simulating real recruiter and technical interviews dynamically.

Workflow

Read Memory
↓

Load Instruction
↓

Build Prompt
↓

Call LLM
↓

Validate Response
↓

Update Memory
↓

Return Result
"""

from typing import Dict, Any
from core.base_skill import BaseSkill
from skills.interview.schema import InterviewOutputSchema
from core.skill_output import UniversalSkillOutput
from core.logger import logger


class InterviewSkill(BaseSkill):
    """
    Skill for simulating real recruiter and technical interviews dynamically.
    Inherits from BaseSkill to maintain consistent architecture.
    """
    
    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        """
        Executes the interview simulation and parses the response into the InterviewOutputSchema.
        Returns UniversalSkillOutput for consistent API responses.
        """
        target_schema = schema or InterviewOutputSchema
        result = await super().execute(context=context, schema=target_schema)
        
        # Ensure result is not a coroutine
        if hasattr(result, '__await__'):
            logger.error("Result is a coroutine, awaiting it...")
            result = await result
        
        # Wrap in universal output format
        universal_output = UniversalSkillOutput(
            status="completed",
            skill="interview",
            current_module="preparation",
            result=result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)},
            evaluation={},
            evidence=[],
            progress=0.6,
            next_action="readiness",
            next_action_reason="Interview simulation completed, evaluating readiness"
        )
        
        return universal_output

