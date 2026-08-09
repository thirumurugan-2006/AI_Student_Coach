"""
Centralised API Router Registration.

All sub-routers are imported and registered here.
main.py uses this single router to keep itself clean.
"""

from fastapi import APIRouter

from api.user import router as user_router
from api.survey import router as survey_router
from api.assessment import router as assessment_router
from api.learning import router as learning_router
from api.interview import router as interview_router
from api.reflection import router as reflection_router
from api.dashboard import router as dashboard_router
from api.career_coach import router as career_coach_router
from api.placement import router as placement_router
from api.workflow import router as workflow_router
from api.skill_gap import router as skill_gap_router
from api.roadmap import router as roadmap_router
from api.readiness import router as readiness_router
from api.placement_aptitude import router as placement_aptitude_router
from api.placement_coding import router as placement_coding_router
from api.placement_technical import router as placement_technical_router
from api.placement_interview import router as placement_interview_router
from api.placement_hr import router as placement_hr_router
from api.placement_report import router as placement_report_router
from api.career_intelligence import router as career_intelligence_router

# ---------------------------------------------------------------------------
# Root API Router
# ---------------------------------------------------------------------------

api_router = APIRouter()

api_router.include_router(user_router, prefix="/user", tags=["User"])
api_router.include_router(survey_router, prefix="/survey", tags=["Career Survey"])
api_router.include_router(assessment_router, prefix="/assessment", tags=["Assessment"])
api_router.include_router(learning_router, prefix="/learning", tags=["Learning"])
api_router.include_router(interview_router, prefix="/interview", tags=["Interview"])
api_router.include_router(reflection_router, prefix="/reflection", tags=["Reflection"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(career_coach_router, prefix="/coach", tags=["Career Coach"])
api_router.include_router(placement_router, prefix="/placement", tags=["Placement"])
api_router.include_router(workflow_router, prefix="/workflow", tags=["Workflow"])
api_router.include_router(skill_gap_router, prefix="/skill_gap", tags=["Skill Gap"])
api_router.include_router(roadmap_router, prefix="/roadmap", tags=["Roadmap"])
api_router.include_router(readiness_router, prefix="/readiness", tags=["Readiness"])
api_router.include_router(placement_aptitude_router, prefix="/placement/aptitude", tags=["Placement Aptitude"])
api_router.include_router(placement_coding_router, prefix="/placement/coding", tags=["Placement Coding"])
api_router.include_router(placement_technical_router, prefix="/placement/technical", tags=["Placement Technical"])
api_router.include_router(placement_interview_router, prefix="/placement/interview", tags=["Placement Interview"])
api_router.include_router(placement_hr_router, prefix="/placement/hr", tags=["Placement HR"])
api_router.include_router(placement_report_router, prefix="/placement/report", tags=["Placement Report"])
api_router.include_router(career_intelligence_router, prefix="/career_intelligence", tags=["Career Intelligence"])
