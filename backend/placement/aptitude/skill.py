"""
Aptitude Skill

Generates personalized aptitude questions based on student profile.
"""

from typing import Dict, Any
from core.base_skill import BaseSkill
from placement.aptitude.schemas import AptitudeOutput


class AptitudeSkill(BaseSkill):
    """
    Skill for generating aptitude questions.
    """

    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        target_schema = schema or AptitudeOutput
        result = await super().execute(context=context, schema=target_schema)
        return result
