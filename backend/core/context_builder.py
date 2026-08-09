from typing import Dict, Any

class ContextBuilder:
    """
    Utility class to help construct formatted contexts for the LLM.
    Separates the logic of formatting data from the main skill logic.
    """
    
    @staticmethod
    def build_skill_context(skill_context_data: Dict[str, Any]) -> str:
        """
        Formats generic key-value context data into a clear readable string.
        
        Args:
            skill_context_data: A dictionary of context variables.
            
        Returns:
            A formatted string representing the context.
        """
        if not skill_context_data:
            return "No additional context provided."
            
        formatted_context = "### Current Interaction Context\n"
        for key, value in skill_context_data.items():
            formatted_context += f"- **{key}**: {value}\n"
            
        return formatted_context
