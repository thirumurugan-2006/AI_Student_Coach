"""
Card Components for Streamlit Demo Frontend.
"""

import streamlit as st
from config import UI_CONFIG


def render_info_card(title: str, content: str, icon: str = "ℹ️"):
    """
    Render an information card.
    
    Args:
        title: Card title
        content: Card content
        icon: Card icon
    """
    with st.container():
        st.markdown(f"### {icon} {title}")
        st.markdown(content)
        st.markdown("---")


def render_stat_card(label: str, value: str, delta: str = None, icon: str = "📊"):
    """
    Render a statistic card.
    
    Args:
        label: Statistic label
        value: Statistic value
        delta: Optional delta value
        icon: Card icon
    """
    with st.container():
        st.metric(label=label, value=value, delta=delta)
        st.caption(icon)
