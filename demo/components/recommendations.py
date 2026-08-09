"""
Recommendations Component for Streamlit Demo Frontend.
"""

import streamlit as st


def render_recommendations(recommendations: dict):
    """
    Render recommendations from the backend.
    
    Args:
        recommendations: Recommendations dictionary from backend
    """
    if not recommendations:
        st.warning("No recommendations available yet.")
        return
    
    st.markdown("## 🎯 Recommendations")
    
    # Priority action
    if "priority_action" in recommendations:
        st.success(f"**Priority Action:** {recommendations['priority_action']}")
    
    st.markdown("---")
    
    # Skill gaps
    if "skill_gap_recommendations" in recommendations and recommendations["skill_gap_recommendations"]:
        st.subheader("📚 Skill Gaps to Address")
        for gap in recommendations["skill_gap_recommendations"]:
            st.markdown(f"- {gap}")
    
    # Learning recommendations
    if "learning_recommendations" in recommendations and recommendations["learning_recommendations"]:
        st.subheader("📖 Learning Topics")
        for topic in recommendations["learning_recommendations"]:
            st.markdown(f"- {topic}")
    
    # Interview recommendations
    if "interview_recommendations" in recommendations and recommendations["interview_recommendations"]:
        st.subheader("💼 Interview Preparation")
        for rec in recommendations["interview_recommendations"]:
            st.markdown(f"- {rec}")
    
    # Career path options
    if "career_path_options" in recommendations and recommendations["career_path_options"]:
        st.subheader("🚀 Career Path Options")
        for path in recommendations["career_path_options"]:
            st.markdown(f"- {path}")
