"""
Technical Skill

Generates personalized technical interview questions.
"""

from typing import Dict, Any
from core.base_skill import BaseSkill
from placement.technical.schemas import TechnicalOutput


class TechnicalSkill(BaseSkill):
    """
    Skill for generating technical interview questions.
    """

    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        target_schema = schema or TechnicalOutput
        result = await super().execute(context=context, schema=target_schema)
        return result
