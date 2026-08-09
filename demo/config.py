"""
Configuration for Streamlit Demo Frontend.
"""

import os
from pathlib import Path

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")

# API Endpoints
API_ENDPOINTS = {
    "health": f"{BACKEND_URL}/health",
    "signup": f"{BACKEND_URL}/user/signup",
    "profile": f"{BACKEND_URL}/user/profile",
    "session": f"{BACKEND_URL}/user/session",
    "logout": f"{BACKEND_URL}/user/logout",
    "survey": f"{BACKEND_URL}/survey/",
    "assessment": f"{BACKEND_URL}/assessment/",
    "skill_gap": f"{BACKEND_URL}/skill_gap/",
    "roadmap": f"{BACKEND_URL}/roadmap/",
    "learning": f"{BACKEND_URL}/learning/",
    "reflection": f"{BACKEND_URL}/reflection/",
    "readiness": f"{BACKEND_URL}/readiness/",
    "placement": f"{BACKEND_URL}/placement",
    "placement_aptitude": f"{BACKEND_URL}/placement/aptitude",
    "placement_coding": f"{BACKEND_URL}/placement/coding",
    "placement_technical": f"{BACKEND_URL}/placement/technical",
    "placement_interview": f"{BACKEND_URL}/placement/interview",
    "placement_hr": f"{BACKEND_URL}/placement/hr",
    "placement_report": f"{BACKEND_URL}/placement/report",
    "interview": f"{BACKEND_URL}/interview/",
    "dashboard": f"{BACKEND_URL}/dashboard/",
    "career_intelligence": f"{BACKEND_URL}/career_intelligence/",
    "coach_chat": f"{BACKEND_URL}/coach/chat",
    "coach_status": f"{BACKEND_URL}/coach/status",
    "coach_skills": f"{BACKEND_URL}/coach/skills",
    "workflow": f"{BACKEND_URL}/workflow/state",
}

# Page Configuration
PAGE_CONFIG = {
    "page_title": "AI Career Coach Demo",
    "page_icon": "🎯",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# UI Configuration
UI_CONFIG = {
    "primary_color": "#1E88E5",
    "secondary_color": "#42A5F5",
    "success_color": "#43A047",
    "warning_color": "#FB8C00",
    "error_color": "#E53935",
    "background_color": "#F5F5F5",
}
