"""
Pipelines Module

Central execution layer for all skills in the AI Career Coach.

The Pipeline layer controls HOW each skill executes, while the
Workflow Controller decides WHAT should happen next.
"""

from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_result import PipelineResult
from pipelines.pipeline_context import PipelineContext

__all__ = [
    "BasePipeline",
    "PipelineResult", 
    "PipelineContext"
]
