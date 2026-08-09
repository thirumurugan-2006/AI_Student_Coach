"""
Progress Component for Streamlit Demo Frontend.
"""

import streamlit as st
from config import UI_CONFIG


def render_progress(current_stage: str, total_stages: int = 6):
    """
    Render workflow progress indicator.
    
    Args:
        current_stage: Current workflow stage
        total_stages: Total number of stages
    """
    stages = ["survey", "assessment", "learning", "interview", "reflection", "dashboard"]
    
    if current_stage not in stages:
        current_stage = "survey"
    
    current_index = stages.index(current_stage)
    progress = (current_index + 1) / total_stages
    
    st.markdown("### Workflow Progress")
    st.progress(progress)
    
    # Stage indicators
    cols = st.columns(total_stages)
    for i, (stage, col) in enumerate(zip(stages, cols)):
        if i < current_index:
            col.success("✅")
        elif i == current_index:
            col.info("🔄")
        else:
            col.caption("⭕")
        col.caption(stage.capitalize())
