"""
Pipeline Registration

Central function to register all pipelines with the PipelineRouter.
This should be called during application startup.
"""

from pipelines.router import pipeline_router
from pipelines.preparation.survey_pipeline import SurveyPipeline
from pipelines.preparation.survey_answer_pipeline import SurveyAnswerPipeline
from pipelines.preparation.assessment_pipeline import AssessmentPipeline
from pipelines.preparation.assessment_answer_pipeline import AssessmentAnswerPipeline
from pipelines.preparation.skill_gap_pipeline import SkillGapPipeline
from pipelines.preparation.roadmap_pipeline import RoadmapPipeline
from pipelines.preparation.learning_pipeline import LearningPipeline
from pipelines.preparation.reflection_pipeline import ReflectionPipeline
from pipelines.preparation.readiness_pipeline import ReadinessPipeline
from pipelines.placement.aptitude_pipeline import AptitudePipeline
from pipelines.placement.coding_pipeline import CodingPipeline
from pipelines.placement.technical_pipeline import TechnicalPipeline
from pipelines.placement.interview_pipeline import InterviewPipeline
from pipelines.placement.hr_pipeline import HRPipeline
from pipelines.placement.placement_report_pipeline import PlacementReportPipeline
from core.logger import logger


def register_all_pipelines():
    """Register all pipelines with the PipelineRouter."""
    logger.info("Registering all pipelines with PipelineRouter")
    
    # Preparation Module Pipelines
    pipeline_router.register_pipeline("survey", SurveyPipeline)
    pipeline_router.register_pipeline("survey_answer", SurveyAnswerPipeline)
    pipeline_router.register_pipeline("assessment", AssessmentPipeline)
    pipeline_router.register_pipeline("assessment_answer", AssessmentAnswerPipeline)
    pipeline_router.register_pipeline("skill_gap", SkillGapPipeline)
    pipeline_router.register_pipeline("roadmap", RoadmapPipeline)
    pipeline_router.register_pipeline("learning", LearningPipeline)
    pipeline_router.register_pipeline("reflection", ReflectionPipeline)
    pipeline_router.register_pipeline("readiness", ReadinessPipeline)
    
    # Placement Module Pipelines
    pipeline_router.register_pipeline("placement_aptitude", AptitudePipeline)
    pipeline_router.register_pipeline("placement_coding", CodingPipeline)
    pipeline_router.register_pipeline("placement_technical", TechnicalPipeline)
    pipeline_router.register_pipeline("placement_interview", InterviewPipeline)
    pipeline_router.register_pipeline("placement_hr", HRPipeline)
    pipeline_router.register_pipeline("placement_report", PlacementReportPipeline)
    
    logger.info(f"All pipelines registered: {pipeline_router.list_registered_pipelines()}")
