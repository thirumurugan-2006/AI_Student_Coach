"""
Skill Gap Skill

Responsible for analyzing assessment results to identify skill gaps.

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
from skills.skill_gap.schema import SkillGapOutput
from core.skill_output import UniversalSkillOutput
from core.logger import logger


class SkillGapSkill(BaseSkill):
    """
    Skill for analyzing assessment results to identify skill gaps.
    Inherits from BaseSkill to maintain consistent architecture.
    """

    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        """
        Executes the skill gap analysis logic and parses the response into the SkillGapOutput schema.
        Returns UniversalSkillOutput for consistent API responses.
        """
        target_schema = schema or SkillGapOutput
        result = await super().execute(context=context, schema=target_schema)
        
        # Ensure result is not a coroutine
        if hasattr(result, '__await__'):
            logger.error("Result is a coroutine, awaiting it...")
            result = await result
        
        # Wrap in universal output format
        universal_output = UniversalSkillOutput(
            status="completed",
            skill="skill_gap",
            current_module="preparation",
            result=result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)},
            evaluation={},
            evidence=[],
            progress=0.3,
            next_action="roadmap",
            next_action_reason="Skill gap analysis completed, generating roadmap"
        )
        
        return universal_output
