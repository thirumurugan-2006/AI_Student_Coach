"""
Reflection Skill

Responsible for asking reflection questions, measuring confidence, and capturing learning insights.

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
from skills.reflection.schema import ReflectionOutputSchema
from core.skill_output import UniversalSkillOutput
from core.logger import logger


class ReflectionSkill(BaseSkill):
    """
    Skill for asking reflection questions, measuring confidence, and capturing learning insights.
    Inherits from BaseSkill to maintain consistent architecture.
    """
    
    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        """
        Executes the reflection capture and parses the response into the ReflectionOutputSchema.
        Returns UniversalSkillOutput for consistent API responses.
        """
        target_schema = schema or ReflectionOutputSchema
        result = await super().execute(context=context, schema=target_schema)
        
        # Ensure result is not a coroutine
        if hasattr(result, '__await__'):
            logger.error("Result is a coroutine, awaiting it...")
            result = await result
        
        # Wrap in universal output format
        universal_output = UniversalSkillOutput(
            status="completed",
            skill="reflection",
            current_module="preparation",
            result=result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)},
            evaluation={},
            evidence=[],
            progress=0.7,
            next_action="readiness",
            next_action_reason="Reflection captured, evaluating readiness"
        )
        
        return universal_output

