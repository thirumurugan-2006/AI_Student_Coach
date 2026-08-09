from typing import Dict, Type
from core.base_skill import BaseSkill
from core.llm_interface import LLMInterface
from memory.student_memory import StudentMemory
from core.logger import logger

class SkillRegistry:
    """
    Dynamic registry for all AI Agent Skills.
    Allows executing skills by name without hardcoding `if/else` logic.
    """
    
    def __init__(self, llm: LLMInterface, memory: StudentMemory):
        self._skills: Dict[str, BaseSkill] = {}
        self.llm = llm
        self.memory = memory

    def register(self, skill_name: str, skill_class: Type[BaseSkill]) -> None:
        """
        Registers a skill class to be instantiated and managed by the registry.
        """
        if skill_name in self._skills:
            logger.warning(f"Skill '{skill_name}' is already registered. Overwriting.")
            
        self._skills[skill_name] = skill_class(llm=self.llm, memory=self.memory)
        logger.info(f"Successfully registered skill: {skill_name}")

    async def execute(self, skill_name: str, context: dict, schema: type = None, student_id: str = None) -> any:
        """
        Executes a registered skill by name.
        """
        if skill_name not in self._skills:
            raise ValueError(f"Skill '{skill_name}' not found in registry.")
            
        logger.info(f"Executing skill: {skill_name} for student: {student_id}")
        skill_instance = self._skills[skill_name]
        
        # Update student_id if provided
        if student_id:
            skill_instance.student_id = student_id
            
        result = await skill_instance.execute(context=context, schema=schema)
        
        # Ensure result is not a coroutine
        if hasattr(result, '__await__'):
            logger.error(f"Result from skill {skill_name} is a coroutine, awaiting it...")
            result = await result
            
        return result
