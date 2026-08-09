"""
Coding Skill

Generates personalized coding problems based on student profile.
"""

from typing import Dict, Any
from core.base_skill import BaseSkill
from placement.coding.schemas import CodingOutput


class CodingSkill(BaseSkill):
    """
    Skill for generating coding problems.
    """

    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        target_schema = schema or CodingOutput
        result = await super().execute(context=context, schema=target_schema)
        return result
