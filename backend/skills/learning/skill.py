"""
Learning Skill

Responsible for building personalized learning roadmaps and recommending resources.

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
from skills.learning.schema import LearningOutputSchema
from core.skill_output import UniversalSkillOutput
from core.logger import logger


class LearningSkill(BaseSkill):
    """
    Skill for building personalized learning roadmaps and recommending resources.
    Inherits from BaseSkill to maintain consistent architecture.
    """
    
    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        """
        Executes the learning plan generation and parses the response into the LearningOutputSchema.
        Returns UniversalSkillOutput for consistent API responses.
        """
        target_schema = schema or LearningOutputSchema
        result = await super().execute(context=context, schema=target_schema)
        
        # Ensure result is not a coroutine
        if hasattr(result, '__await__'):
            logger.error("Result is a coroutine, awaiting it...")
            result = await result
        
        # Wrap in universal output format
        universal_output = UniversalSkillOutput(
            status="completed",
            skill="learning",
            current_module="preparation",
            result=result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)},
            evaluation={},
            evidence=[],
            progress=0.5,
            next_action="reflection",
            next_action_reason="Learning plan generated, requesting reflection"
        )
        
        return universal_output

