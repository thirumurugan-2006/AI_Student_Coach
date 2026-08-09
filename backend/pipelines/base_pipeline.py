"""
BasePipeline

Base class for all Pipeline implementations.
Defines the standard lifecycle that every Pipeline must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from core.logger import logger


class BasePipeline(ABC):
    """
    Base class for all Pipeline implementations.
    
    Every Pipeline must implement the execute method and follow
    the standard lifecycle:
    1. Load workflow state
    2. Load student context
    3. Load career intelligence
    4. Load skill instructions
    5. Load previous activity
    6. Load question history
    7. Execute skill
    8. Call LLM if required
    9. Parse response
    10. Validate response
    11. Store result
    12. Wait for student input if required
    13. Evaluate
    14. Create evidence
    15. Update student memory
    16. Update career intelligence
    17. Update database
    18. Ask planner for next action
    19. Validate next action
    20. Return PipelineResult
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """
        Initialize the Pipeline with required dependencies.
        
        Args:
            llm: LLM interface for content generation
            memory: Student memory for persistence
            career_intelligence: Career intelligence hub
        """
        self.llm = llm
        self.memory = memory
        self.career_intelligence = career_intelligence
        self.pipeline_name = self.__class__.__name__.replace("Pipeline", "").lower()
    
    @abstractmethod
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Pipeline with the given context.
        
        Args:
            context: PipelineContext containing all necessary information
            
        Returns:
            PipelineResult with execution results
        """
        pass
    
    async def load_workflow_state(self, context: PipelineContext) -> PipelineContext:
        """Load current workflow state."""
        logger.info(f"{self.pipeline_name}: Loading workflow state")
        # Workflow state is loaded by the Workflow Controller
        # This method can be used to validate or enrich the state
        return context
    
    async def load_student_context(self, context: PipelineContext) -> PipelineContext:
        """Load student context from memory."""
        logger.info(f"{self.pipeline_name}: Loading student context")
        if self.memory and context.student_id:
            profile = self.memory.get_profile(context.student_id)
            if profile:
                context.student_memory = profile
        return context
    
    async def load_career_intelligence(self, context: PipelineContext) -> PipelineContext:
        """Load career intelligence data."""
        logger.info(f"{self.pipeline_name}: Loading career intelligence")
        if self.career_intelligence and context.student_id:
            intelligence = self.career_intelligence.get_student_intelligence(context.student_id)
            if intelligence:
                context.career_intelligence = intelligence
        return context
    
    async def load_skill_instructions(self, context: PipelineContext) -> str:
        """Load skill-specific instructions."""
        logger.info(f"{self.pipeline_name}: Loading skill instructions")
        # This should be implemented by each specific pipeline
        return ""
    
    async def load_previous_activity(self, context: PipelineContext) -> PipelineContext:
        """Load previous activity for the student."""
        logger.info(f"{self.pipeline_name}: Loading previous activity")
        return context
    
    async def load_question_history(self, context: PipelineContext) -> PipelineContext:
        """Load question history for uniqueness checking."""
        logger.info(f"{self.pipeline_name}: Loading question history")
        return context
    
    async def validate_result(self, result: Any) -> bool:
        """Validate the result from skill execution."""
        logger.debug(f"{self.pipeline_name}: Validating result")
        return result is not None
    
    async def persist_memory(self, context: PipelineContext) -> bool:
        """Persist in-memory student profile to database when a session is available."""
        if not self.memory or not context.student_id:
            return False
        db = context.additional_context.get("db_session")
        if db is not None:
            await self.memory.save(db, context.student_id)
            return True
        return False

    async def persist_result(self, context: PipelineContext, result: Any) -> bool:
        """Persist the result to database."""
        logger.info(f"{self.pipeline_name}: Persisting result")
        return await self.persist_memory(context)
    
    async def evaluate_result(self, context: PipelineContext, result: Any) -> Dict[str, Any]:
        """Evaluate the result and create evidence."""
        logger.info(f"{self.pipeline_name}: Evaluating result")
        return {}
    
    async def update_student_memory(self, context: PipelineContext, result: Any) -> bool:
        """Update student memory with new information."""
        logger.info(f"{self.pipeline_name}: Updating student memory")
        # Skip memory update for now - the save method requires db session
        # This will be addressed in a future step
        return True
    
    async def update_career_intelligence(self, context: PipelineContext, result: Any) -> bool:
        """Update career intelligence with new evidence."""
        logger.info(f"{self.pipeline_name}: Updating career intelligence")
        if self.career_intelligence and context.student_id:
            if hasattr(self.career_intelligence, "update_intelligence"):
                self.career_intelligence.update_intelligence(context.student_id, result)
            elif isinstance(result, dict) and "evidence" in result:
                for ev in result["evidence"]:
                    if isinstance(ev, dict):
                        self.career_intelligence.add_evidence(
                            context.student_id,
                            evidence_type=ev.get("type", self.pipeline_name),
                            skill=ev.get("skill", "general"),
                            score=float(ev.get("score", 1.0 if ev.get("is_correct") else 0.0)),
                            is_correct=ev.get("is_correct"),
                            metadata=ev,
                        )
        return True
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """
        Determine the next action and reason.
        
        Returns:
            Tuple of (next_action, next_action_reason)
        """
        logger.info(f"{self.pipeline_name}: Determining next action")
        # This should be implemented by specific pipelines or use the Planner
        return "dashboard", "Pipeline completed"
    
    async def create_pipeline_result(
        self,
        context: PipelineContext,
        status: str,
        result: Dict[str, Any],
        evaluation: Dict[str, Any],
        evidence: list,
        progress: float,
        next_action: str,
        next_action_reason: str,
        error_message: str = None
    ) -> PipelineResult:
        """Create a PipelineResult object."""
        return PipelineResult(
            status=status,
            pipeline=self.pipeline_name,
            skill=self.pipeline_name,
            current_module=context.current_module if hasattr(context, 'current_module') else "preparation",
            result=result,
            evaluation=evaluation,
            evidence=evidence,
            progress=progress,
            next_action=next_action,
            next_action_reason=next_action_reason,
            error_message=error_message
        )
