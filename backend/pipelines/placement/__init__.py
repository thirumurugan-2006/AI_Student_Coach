"""
Placement Pipelines

Pipelines for the Placement Simulation module:
- Aptitude
- Coding
- Technical
- Interview
- HR
- Placement Report
"""

from pipelines.placement.aptitude_pipeline import AptitudePipeline
from pipelines.placement.coding_pipeline import CodingPipeline
from pipelines.placement.technical_pipeline import TechnicalPipeline
from pipelines.placement.interview_pipeline import InterviewPipeline
from pipelines.placement.hr_pipeline import HRPipeline
from pipelines.placement.placement_report_pipeline import PlacementReportPipeline

__all__ = [
    "AptitudePipeline",
    "CodingPipeline",
    "TechnicalPipeline",
    "InterviewPipeline",
    "HRPipeline",
    "PlacementReportPipeline"
]
