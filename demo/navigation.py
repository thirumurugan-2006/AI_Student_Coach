"""
Centralized Navigation Resolver for AI Career Coach Frontend

Maps backend workflow states to frontend pages and renderers.
Ensures consistent navigation across the application.
"""

from typing import Callable, Dict, Optional
import streamlit as st


# Module registry mapping next_action to render functions
MODULE_REGISTRY: Dict[str, Callable] = {
    "survey": None,  # Will be set to render_survey_stage
    "assessment": None,  # Will be set to render_assessment_stage
    "skill_gap": None,  # Will be set to render_skill_gap_stage
    "roadmap": None,  # Will be set to render_roadmap_stage
    "learning": None,  # Will be set to render_learning_stage
    "reflection": None,  # Will be set to render_reflection_stage
    "readiness": None,  # Will be set to render_readiness_stage
    "placement_aptitude": None,  # Will be set to render_placement_aptitude_stage
    "placement_coding": None,  # Will be set to render_placement_coding_stage
    "placement_technical": None,  # Will be set to render_placement_technical_stage
    "placement_interview": None,  # Will be set to render_placement_interview_stage
    "placement_hr": None,  # Will be set to render_placement_hr_stage
    "placement_report": None,  # Will be set to render_placement_report_stage
    "dashboard": None,  # Will be set to render_dashboard_stage
    "career_intelligence": None,  # Will be set to render_career_intelligence_stage
}


def register_module(action: str, renderer: Callable) -> None:
    """
    Register a module renderer for a given action.
    
    Args:
        action: The backend action name (e.g., "survey", "assessment")
        renderer: The Streamlit render function for this module
    """
    MODULE_REGISTRY[action] = renderer


def resolve_navigation(next_action: str) -> str:
    """
    Resolve backend next_action to frontend page/stage.
    
    Args:
        next_action: The action returned by the backend planner
        
    Returns:
        The frontend stage name to render
    """
    # Map backend actions to frontend stages
    action_to_stage = {
        "survey": "survey",
        "assessment": "assessment",
        "skill_gap": "skill_gap",
        "roadmap": "roadmap",
        "learning": "learning",
        "reflection": "reflection",
        "readiness": "readiness",
        "placement_aptitude": "placement_aptitude",
        "placement_coding": "placement_coding",
        "placement_technical": "placement_technical",
        "placement_interview": "placement_interview",
        "placement_hr": "placement_hr",
        "placement_report": "placement_report",
        "dashboard": "dashboard",
        "career_intelligence": "career_intelligence",
    }
    
    return action_to_stage.get(next_action, "dashboard")


def navigate_to_stage(stage: str) -> None:
    """
    Navigate to a specific stage by updating session state.
    
    Args:
        stage: The target stage name
    """
    st.session_state["current_stage"] = stage
    st.rerun()


def handle_workflow_transition(next_action: Optional[str]) -> None:
    """
    Handle workflow transition based on backend next_action.
    
    Args:
        next_action: The next action from backend planner
    """
    if not next_action:
        # Default to dashboard if no action specified
        navigate_to_stage("dashboard")
        return
    
    target_stage = resolve_navigation(next_action)
    navigate_to_stage(target_stage)


def get_current_stage_info() -> Dict[str, str]:
    """
    Get information about the current stage.
    
    Returns:
        Dictionary with stage metadata
    """
    stage = st.session_state.get("current_stage", "dashboard")
    
    stage_info = {
        "survey": {"name": "Career Discovery Survey", "icon": "🎯", "module": "Career Preparation"},
        "assessment": {"name": "Skill Assessment", "icon": "📝", "module": "Career Preparation"},
        "skill_gap": {"name": "Skill Gap Analysis", "icon": "🔍", "module": "Career Preparation"},
        "roadmap": {"name": "Learning Roadmap", "icon": "🗺️", "module": "Career Preparation"},
        "learning": {"name": "Personalized Learning", "icon": "📚", "module": "Career Preparation"},
        "reflection": {"name": "Growth Reflection", "icon": "🤔", "module": "Career Preparation"},
        "readiness": {"name": "Readiness Gate", "icon": "🚪", "module": "Career Preparation"},
        "placement_aptitude": {"name": "Aptitude Round", "icon": "🧠", "module": "Placement Simulation"},
        "placement_coding": {"name": "Coding Round", "icon": "�", "module": "Placement Simulation"},
        "placement_technical": {"name": "Technical Round", "icon": "⚙️", "module": "Placement Simulation"},
        "placement_interview": {"name": "Interview Round", "icon": "🎤", "module": "Placement Simulation"},
        "placement_hr": {"name": "HR Round", "icon": "👥", "module": "Placement Simulation"},
        "placement_report": {"name": "Placement Report", "icon": "📄", "module": "Placement Simulation"},
        "dashboard": {"name": "Dashboard", "icon": "📊", "module": "Career Intelligence"},
        "career_intelligence": {"name": "Career Intelligence", "icon": "🧠", "module": "Career Intelligence"},
    }
    
    return stage_info.get(stage, {"name": "Dashboard", "icon": "📊", "module": "Career Intelligence"})


def get_module_stages(module: str) -> list:
    """
    Get all stages belonging to a module.
    
    Args:
        module: The module name ("Career Preparation" or "Placement Simulation")
        
    Returns:
        List of stage names in the module
    """
    module_stages = {
        "Career Preparation": ["survey", "assessment", "skill_gap", "roadmap", "learning", "reflection", "readiness"],
        "Placement Simulation": ["placement_aptitude", "placement_coding", "placement_technical", "placement_interview", "placement_hr", "placement_report"],
        "Career Intelligence": ["dashboard", "career_intelligence"],
    }
    
    return module_stages.get(module, [])
