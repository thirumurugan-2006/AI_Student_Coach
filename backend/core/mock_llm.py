"""
Mock LLM for testing without calling Groq
Provides deterministic responses for testing
"""
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel
import asyncio
import json


class MockLLM:
    """
    Mock LLM that returns deterministic test responses.
    Used for testing pipeline, skill, validation, database, memory without calling Groq.
    Implements the same interface as ContentLLM for compatibility.
    """
    
    def __init__(self):
        self.call_count = 0
    
    async def health_check(self) -> Dict[str, Any]:
        """Mock health check - always returns healthy"""
        return {
            "content_llm": True,
            "planning_llm": True
        }
    
    async def generate(
        self,
        prompt: str,
        schema: Optional[type[BaseModel]] = None,
        stream: bool = False
    ) -> Union[BaseModel, str]:
        """
        Generate mock response based on prompt content.
        Returns deterministic test data for survey questions.
        Compatible with ContentLLM interface.
        """
        self.call_count += 1
        
        # Return mock survey question
        if "survey" in prompt.lower():
            response_text = """{
  "question_type": "mcq",
  "status": "success",
  "survey_completed": false,
  "profile": {
    "career_goal": null,
    "target_company": null,
    "experience_level": null,
    "primary_language": null,
    "known_skills": [],
    "projects": 0,
    "study_hours": 1,
    "learning_style": null,
    "weak_topics": [],
    "timeline": null
  },
  "confidence": 0.5,
  "missing_information": ["career_goal", "experience_level"],
  "mcq_question_content": {
    "question": "Which area of technology interests you most?",
    "options": [
      "AI/ML",
      "Web Development", 
      "Data Science",
      "Cybersecurity"
    ]
  },
  "next_action": "survey",
  "next_action_reason": "Continue survey"
}"""
            
            # If schema is provided, try to parse and validate
            if schema:
                try:
                    data = json.loads(response_text)
                    return schema(**data)
                except Exception as e:
                    print(f"MockLLM: Failed to parse schema: {e}")
                    # Return string as fallback
                    return response_text
            
            return response_text
        
        # Return mock assessment question
        elif "assessment" in prompt.lower():
            response_text = """{
  "question_type": "mcq",
  "mcq_question_content": {
    "question": "What is the time complexity of binary search?",
    "options": [
      "O(n)",
      "O(log n)",
      "O(n^2)",
      "O(1)"
    ],
    "correct_option_index": 1
  },
  "assessment_completed": false,
  "next_action": "assessment"
}"""
            
            if schema:
                try:
                    data = json.loads(response_text)
                    return schema(**data)
                except:
                    pass
            
            return response_text
        
        # Default response
        response_text = """{
  "status": "success",
  "next_action": "continue"
}"""
        
        if schema:
            try:
                data = json.loads(response_text)
                return schema(**data)
            except:
                pass
        
        return response_text
