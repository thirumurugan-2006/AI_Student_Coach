"""
Session State Management for Streamlit Demo Frontend.
"""

import streamlit as st


def init_session_state():
    """
    Initialize Streamlit session state.
    """
    # Backend health
    if "backend_healthy" not in st.session_state:
        st.session_state["backend_healthy"] = False
    
    # User session
    if "user" not in st.session_state:
        st.session_state["user"] = None
    
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    
    if "access_token" not in st.session_state:
        st.session_state["access_token"] = None
    
    # Workflow state - driven by backend
    if "current_stage" not in st.session_state:
        st.session_state["current_stage"] = "onboarding"
    
    if "next_action" not in st.session_state:
        st.session_state["next_action"] = None
    
    if "workflow_progress" not in st.session_state:
        st.session_state["workflow_progress"] = 0
    
    # Backend workflow state cache
    if "backend_workflow_state" not in st.session_state:
        st.session_state["backend_workflow_state"] = None
    
    # Skill-specific state (temporary UI state only)
    if "current_mcq" not in st.session_state:
        st.session_state["current_mcq"] = None
    
    if "assessment_question" not in st.session_state:
        st.session_state["assessment_question"] = None
    
    if "assessment_topic" not in st.session_state:
        st.session_state["assessment_topic"] = None
    
    if "interview_question" not in st.session_state:
        st.session_state["interview_question"] = None
    
    if "interview_company" not in st.session_state:
        st.session_state["interview_company"] = None
    
    if "interview_role" not in st.session_state:
        st.session_state["interview_role"] = None
    
    # History (temporary display only)
    if "survey_history" not in st.session_state:
        st.session_state["survey_history"] = []
    
    if "assessment_history" not in st.session_state:
        st.session_state["assessment_history"] = []
    
    if "interview_history" not in st.session_state:
        st.session_state["interview_history"] = []
    
    if "reflection_notes" not in st.session_state:
        st.session_state["reflection_notes"] = []
    
    # Result caches (temporary display only)
    if "skill_gap_result" not in st.session_state:
        st.session_state["skill_gap_result"] = None
    
    if "roadmap_result" not in st.session_state:
        st.session_state["roadmap_result"] = None
    
    if "readiness_result" not in st.session_state:
        st.session_state["readiness_result"] = None
    
    # Legacy compatibility - keep these for now
    if "learning_roadmap" not in st.session_state:
        st.session_state["learning_roadmap"] = None
    
    if "placement_assessment" not in st.session_state:
        st.session_state["placement_assessment"] = None
    
    # Dashboard data cache
    if "dashboard_data" not in st.session_state:
        st.session_state["dashboard_data"] = None


def reset_session_state():
    """
    Reset session state (logout).
    """
    st.session_state["user"] = None
    st.session_state["user_id"] = None
    st.session_state["access_token"] = None
    st.session_state["current_stage"] = "onboarding"
    st.session_state["next_action"] = None
    st.session_state["workflow_progress"] = 0
    st.session_state["backend_workflow_state"] = None
    st.session_state["current_mcq"] = None
    st.session_state["assessment_question"] = None
    st.session_state["assessment_topic"] = None
    st.session_state["interview_question"] = None
    st.session_state["interview_company"] = None
    st.session_state["interview_role"] = None
    st.session_state["survey_history"] = []
    st.session_state["assessment_history"] = []
    st.session_state["interview_history"] = []
    st.session_state["reflection_notes"] = []
    st.session_state["skill_gap_result"] = None
    st.session_state["roadmap_result"] = None
    st.session_state["readiness_result"] = None
    st.session_state["learning_roadmap"] = None
    st.session_state["placement_assessment"] = None
    st.session_state["dashboard_data"] = None
