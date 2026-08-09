import os
from typing import Any, Dict
from pydantic import BaseModel
from pathlib import Path
from core.logger import logger

from core.llm_interface import LLMInterface
from memory.student_memory import StudentMemory

class BaseSkill:
    """
    Base class for all skills in the AI Career Coach Agent.
    Implements the core reasoning loop for each skill:
    1. Load instructions and examples
    2. Read Student Memory
    3. Build prompt
    4. Call LLM Interface
    5. Validate & Return
    """
    
    def __init__(self, llm: LLMInterface, memory: StudentMemory, student_id: str = None):
        self.llm = llm
        self.memory = memory
        self.student_id = student_id
        self.skill_name = self.__class__.__name__.replace("Skill", "").lower()
        self._load_prompts()
        
    def _load_prompts(self):
        """Loads instruction.md and examples.md for the specific skill."""
        # Assuming skill files are in backend/skills/<skill_name>/
        base_path = Path(__file__).parent.parent / "skills" / self.skill_name
        
        instruction_path = base_path / "instruction.md"
        examples_path = base_path / "examples.md"
        
        self.instruction = ""
        self.examples = ""
        
        if instruction_path.exists():
            with open(instruction_path, "r", encoding="utf-8") as f:
                self.instruction = f.read()
                
        if examples_path.exists():
            with open(examples_path, "r", encoding="utf-8") as f:
                self.examples = f.read()

    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """Constructs the full prompt by combining memory, instructions, and examples."""
        student_profile = self.memory.get_profile_summary(self.student_id)
        
        prompt = f"Student Profile:\n{student_profile}\n\n"
        prompt += f"Context:\n{context}\n\n"
        prompt += f"Instructions:\n{self.instruction}\n\n"
        prompt += f"Examples:\n{self.examples}\n\n"
        
        return prompt

    async def execute(self, context: Dict[str, Any], schema: type[BaseModel] | None = None) -> BaseModel | str:
        """
        Main execution loop for the skill.
        
        Args:
            context: The input context/request for the skill.
            schema: Optional Pydantic model for structured output.
            
        Returns:
            Structured output or raw string from LLM.
        """
        logger.info(f"{self.skill_name}: BaseSkill.execute() called with context: {context}")
        logger.info(f"{self.skill_name}: Target schema: {schema}")
        
        # 1 & 2 are handled in initialization and _build_prompt
        # 3. Build Prompt
        try:
            prompt = self._build_prompt(context)
            logger.info(f"{self.skill_name}: Prompt built successfully, length: {len(prompt)}")
        except Exception as e:
            logger.error(f"{self.skill_name}: Failed to build prompt: {e}", exc_info=True)
            raise
        
        # 4 & 5. Call LLM Interface and Validate (Assuming LLM interface handles basic validation to schema)
        logger.info(f"{self.skill_name}: Calling LLM.generate with schema: {schema}")
        try:
            result = await self.llm.generate(prompt, schema)
            logger.info(f"{self.skill_name}: LLM.generate returned type: {type(result)}")
        except Exception as e:
            logger.error(f"{self.skill_name}: LLM.generate failed: {e}", exc_info=True)
            raise
        
        # Ensure result is not a coroutine
        if hasattr(result, '__await__'):
            logger.error(f"Result from LLM is a coroutine, awaiting it...")
            result = await result
            logger.debug(f"{self.skill_name}: After await, result type: {type(result)}")
        
        return result
