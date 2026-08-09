"""
Formatting Utilities for Streamlit Demo Frontend.
"""


def format_readiness_score(score: float) -> str:
    """
    Format readiness score for display.
    
    Args:
        score: Readiness score (0-100)
        
    Returns:
        Formatted string
    """
    if score >= 80:
        return f"{score:.1f}% - Ready"
    elif score >= 60:
        return f"{score:.1f}% - Progressing"
    elif score >= 30:
        return f"{score:.1f}% - Needs Work"
    else:
        return f"{score:.1f}% - Starting"


def format_stage_name(stage: str) -> str:
    """
    Format stage name for display.
    
    Args:
        stage: Stage name
        
    Returns:
        Formatted stage name
    """
    stage_map = {
        "onboarding": "Onboarding",
        "survey": "Career Survey",
        "assessment": "Skill Assessment",
        "learning": "Learning Roadmap",
        "interview": "Mock Interview",
        "reflection": "Reflection",
        "dashboard": "Dashboard"
    }
    return stage_map.get(stage, stage.capitalize())


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
