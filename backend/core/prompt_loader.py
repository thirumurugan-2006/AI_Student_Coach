from pathlib import Path
from typing import Tuple

class PromptLoader:
    """
    Utility class for loading markdown prompts and instructions.
    Follows Clean Architecture by isolating file I/O for prompt management.
    """
    
    @staticmethod
    def load_skill_prompts(skill_name: str) -> Tuple[str, str]:
        """
        Loads the instruction.md and examples.md for a given skill.
        
        Args:
            skill_name: The name of the skill (e.g., 'survey', 'assessment').
            
        Returns:
            A tuple containing (instruction_text, examples_text).
        """
        base_path = Path(__file__).parent.parent / "skills" / skill_name
        
        instruction_path = base_path / "instruction.md"
        examples_path = base_path / "examples.md"
        
        instruction = ""
        examples = ""
        
        if instruction_path.exists():
            with open(instruction_path, "r", encoding="utf-8") as f:
                instruction = f.read()
                
        if examples_path.exists():
            with open(examples_path, "r", encoding="utf-8") as f:
                examples = f.read()
                
        return instruction, examples
