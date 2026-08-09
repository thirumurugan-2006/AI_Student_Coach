"""
Error Handling Utilities for Streamlit Demo Frontend.
"""

import streamlit as st
from contextlib import contextmanager


def handle_api_error(error: Exception, context: str = "API Request"):
    """
    Handle API errors with user-friendly messages.
    
    Args:
        error: Exception object
        context: Context of the error
    """
    error_message = str(error)
    
    if "timeout" in error_message.lower():
        st.error("⏱️ Request timed out. The AI is taking longer than expected. Please try again.")
    elif "connection" in error_message.lower():
        st.error("🔌 Cannot connect to the backend. Please ensure the backend is running.")
    elif "authentication" in error_message.lower() or "401" in error_message:
        st.error("🔐 Authentication required. Please log in again.")
    elif "not found" in error_message.lower() or "404" in error_message:
        st.error("🔍 Resource not found. Please check your input.")
    elif "invalid request" in error_message.lower() or "422" in error_message:
        st.error("❌ Invalid request. Please check your input and try again.")
    elif "backend error" in error_message.lower() or "500" in error_message:
        st.error("⚠️ Backend error occurred. Please try again later.")
    else:
        st.error(f"❌ {context} failed: {error_message}")
    
    st.error(f"Debug info: {error_message}")


@contextmanager
def show_loading(message: str = "Processing..."):
    """
    Show a loading spinner with message.
    
    Args:
        message: Loading message
    """
    with st.spinner(f"⏳ {message}"):
        yield


def show_success(message: str):
    """
    Show a success message.
    
    Args:
        message: Success message
    """
    st.success(f"✅ {message}")


def show_warning(message: str):
    """
    Show a warning message.
    
    Args:
        message: Warning message
    """
    st.warning(f"⚠️ {message}")
