"""
Sidebar Component for Streamlit Demo Frontend.
"""

import streamlit as st
from config import UI_CONFIG
from navigation import get_current_stage_info, get_module_stages


def render_sidebar():
    """
    Render the sidebar with navigation and user info.
    """
    with st.sidebar:
        st.title("🎯 AI Career Coach")
        st.markdown("---")
        
        # User info if logged in
        if "user" in st.session_state and st.session_state["user"]:
            user = st.session_state["user"]
            st.success(f"✅ Logged in as: {user.get('name', 'User')}")
            st.caption(f"📧 {user.get('email', '')}")
            st.markdown("---")
        
        # Get current stage info
        current_stage = st.session_state.get("current_stage", "dashboard")
        stage_info = get_current_stage_info()
        
        # Current Stage Header
        st.subheader("Current Stage")
        st.markdown(f"{stage_info.get('icon', '📊')} {stage_info.get('name', 'Dashboard')}")
        st.markdown("---")
        
        # Career Preparation Module
        st.subheader("CAREER PREPARATION")
        
        career_prep_stages = get_module_stages("Career Preparation")
        for stage in career_prep_stages:
            stage_name = stage.replace("_", " ").title()
            if stage == current_stage:
                st.markdown(f"→ **{stage_name}**")
            elif is_stage_accessible(stage, current_stage, career_prep_stages):
                if st.button(stage_name, key=f"nav_{stage}", use_container_width=True):
                    st.session_state["current_stage"] = stage
                    st.rerun()
            else:
                st.markdown(f"� {stage_name}")
        
        st.markdown("---")
        
        # Placement Simulation Module
        st.subheader("PLACEMENT SIMULATION")
        
        placement_stages = get_module_stages("Placement Simulation")
        for stage in placement_stages:
            stage_name = stage.replace("_", " ").title()
            if stage == current_stage:
                st.markdown(f"→ **{stage_name}**")
            elif is_stage_accessible(stage, current_stage, placement_stages):
                if st.button(stage_name, key=f"nav_{stage}", use_container_width=True):
                    st.session_state["current_stage"] = stage
                    st.rerun()
            else:
                st.markdown(f"🔒 {stage_name}")
        
        st.markdown("---")
        
        # Career Intelligence Module
        st.subheader("CAREER INTELLIGENCE")
        
        ci_stages = get_module_stages("Career Intelligence")
        for stage in ci_stages:
            stage_name = stage.replace("_", " ").title()
            if stage == current_stage:
                st.markdown(f"→ **{stage_name}**")
            elif is_stage_accessible(stage, current_stage, ci_stages):
                if st.button(stage_name, key=f"nav_{stage}", use_container_width=True):
                    st.session_state["current_stage"] = stage
                    st.rerun()
            else:
                st.markdown(f"🔒 {stage_name}")
        
        st.markdown("---")
        
        # Progress from backend
        if "workflow_progress" in st.session_state:
            progress = st.session_state["workflow_progress"]
            st.progress(progress / 100)
            st.caption(f"Progress: {progress}%")
        
        st.markdown("---")
        
        # Backend status
        if "backend_healthy" in st.session_state:
            if st.session_state["backend_healthy"]:
                st.success("✅ Backend Online")
            else:
                st.error("❌ Backend Offline")


def is_stage_accessible(stage: str, current_stage: str, module_stages: list) -> bool:
    """
    Check if a stage is accessible based on current stage.
    
    Args:
        stage: The stage to check
        current_stage: The current stage
        module_stages: All stages in the module
        
    Returns:
        True if the stage is accessible, False otherwise
    """
    # For now, allow all stages to be accessible for development
    # In production, this would check backend workflow state
    return True
