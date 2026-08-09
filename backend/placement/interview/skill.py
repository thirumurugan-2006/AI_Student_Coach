"""
Interview Skill

Generates personalized interview questions.
"""

from typing import Dict, Any
from core.base_skill import BaseSkill
from placement.interview.schemas import InterviewOutput


class InterviewSkill(BaseSkill):
    """
    Skill for generating interview questions.
    """

    async def execute(self, context: Dict[str, Any], schema: type = None) -> Any:
        target_schema = schema or InterviewOutput
        result = await super().execute(context=context, schema=target_schema)
        return result
