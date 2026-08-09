"""
HR Skill

Generates personalized HR/behavioral interview questions.
"""

from typing import Dict, Any
from core.base_skill import BaseSkill
from placement.hr.schemas import HROutput


class HRSkill(BaseSkill):
    """
    Skill for generating HR/behavioral interview questions.
    """

    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        target_schema = schema or HROutput
        result = await super().execute(context=context, schema=target_schema)
        return result
