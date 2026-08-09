"""
Chart Components for Streamlit Demo Frontend.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


def render_readiness_chart(readiness_score: float):
    """
    Render a readiness score gauge chart.
    
    Args:
        readiness_score: Readiness score (0-100)
    """
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = readiness_score,
        title = {'text': "Readiness Score"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#1E88E5"},
            'steps': [
                {'range': [0, 30], 'color': "#E53935"},
                {'range': [30, 60], 'color': "#FB8C00"},
                {'range': [60, 80], 'color': "#42A5F5"},
                {'range': [80, 100], 'color': "#43A047"}
            ],
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)


def render_progress_chart(roadmap: list, completed: list):
    """
    Render a learning progress chart.
    
    Args:
        roadmap: List of roadmap topics
        completed: List of completed topics
    """
    if not roadmap:
        st.warning("No roadmap data available.")
        return
    
    # Calculate progress
    total = len(roadmap)
    done = len(completed)
    progress = (done / total * 100) if total > 0 else 0
    
    # Create progress data
    data = {
        "Status": ["Completed", "Remaining"],
        "Count": [done, total - done]
    }
    
    fig = px.pie(
        data,
        values="Count",
        names="Status",
        title=f"Learning Progress: {progress:.1f}%"
    )
    
    st.plotly_chart(fig, use_container_width=True)
