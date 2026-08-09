"""
Roadmap Skill

Responsible for creating personalized learning roadmaps based on skill gaps.

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
from skills.roadmap.schema import RoadmapOutput
from core.skill_output import UniversalSkillOutput
from core.logger import logger


class RoadmapSkill(BaseSkill):
    """
    Skill for creating personalized learning roadmaps.
    Inherits from BaseSkill to maintain consistent architecture.
    """

    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        """
        Executes the roadmap creation logic and parses the response into the RoadmapOutput schema.
        Returns UniversalSkillOutput for consistent API responses.
        """
        target_schema = schema or RoadmapOutput
        result = await super().execute(context=context, schema=target_schema)
        
        # Ensure result is not a coroutine
        if hasattr(result, '__await__'):
            logger.error("Result is a coroutine, awaiting it...")
            result = await result
        
        # Wrap in universal output format
        universal_output = UniversalSkillOutput(
            status="completed",
            skill="roadmap",
            current_module="preparation",
            result=result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)},
            evaluation={},
            evidence=[],
            progress=0.4,
            next_action="learning",
            next_action_reason="Roadmap generated, starting learning phase"
        )
        
        return universal_output
