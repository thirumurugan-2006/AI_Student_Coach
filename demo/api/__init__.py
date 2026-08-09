"""
API Services Package for Streamlit Demo Frontend.
"""

from api.client import client, APIClient
from api.user import user_service, UserService
from api.survey import survey_service, SurveyService
from api.assessment import assessment_service, AssessmentService
from api.skill_gap import skill_gap_service, SkillGapService
from api.roadmap import roadmap_service, RoadmapService
from api.learning import learning_service, LearningService
from api.interview import interview_service, InterviewService
from api.reflection import reflection_service, ReflectionService
from api.readiness import readiness_service, ReadinessService
from api.dashboard import dashboard_service, DashboardService
from api.placement import placement_service, PlacementService
from api.career_intelligence import career_intelligence_service, CareerIntelligenceService
from api.coach import coach_service, CoachService
from api.workflow import workflow_service, WorkflowService

__all__ = [
    'client',
    'APIClient',
    'user_service',
    'UserService',
    'survey_service',
    'SurveyService',
    'assessment_service',
    'AssessmentService',
    'skill_gap_service',
    'SkillGapService',
    'roadmap_service',
    'RoadmapService',
    'learning_service',
    'LearningService',
    'interview_service',
    'InterviewService',
    'reflection_service',
    'ReflectionService',
    'readiness_service',
    'ReadinessService',
    'dashboard_service',
    'DashboardService',
    'placement_service',
    'PlacementService',
    'career_intelligence_service',
    'CareerIntelligenceService',
    'coach_service',
    'CoachService',
    'workflow_service',
    'WorkflowService',
]
