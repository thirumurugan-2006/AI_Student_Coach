from typing import Dict, Any, Type, Optional
from pydantic import BaseModel
from memory.student_memory import StudentMemory
from agent.registry import SkillRegistry
from agent.planner import Planner
from evaluation.evaluation_engine import EvaluationEngine
from core.llm_interface import LLMInterface
from core.logger import logger
from core.workflow_controller import workflow_controller
from services.career_intelligence import CareerIntelligenceHub
from services.readiness_gate import ReadinessGate
from pipelines.pipeline_context import PipelineContext
from pipelines.router import PipelineRouter

class CareerCoach:
    """
    Main Orchestrator Agent.
    
    Responsibilities:
    - Receive requests.
    - Read Planner output for workflow guidance.
    - Reason about the next goal.
    - Execute the appropriate skill using the registry.
    - Route the results to the Evaluation Engine.
    - Return the final response.
    
    Business logic inside the skills is strictly isolated from this orchestrator.
    The Planner controls workflow orchestration.
    The Career Coach reasons about goals.
    The Router executes skills.
    """
    
    def __init__(self, memory: StudentMemory, llm: LLMInterface = None, pipeline_router: Optional[PipelineRouter] = None):
        """
        Initializes the Career Coach with memory and LLM.
        Note: llm can be injected later if needed, but registry needs it.
        """
        self.memory = memory
        self.llm = llm  # Ensure an implementation of LLMInterface is provided in production
        self.pipeline_router = pipeline_router  # Pipeline Router for execution
        
        # Initialize Planner, Registry and Evaluation Engine
        self.planner = Planner(memory=self.memory, llm=llm)
        self.registry = SkillRegistry(llm=self.llm, memory=self.memory)
        self.evaluation_engine = EvaluationEngine(memory=self.memory)
        
        # Initialize Career Intelligence Hub and Readiness Gate
        self.career_intelligence = CareerIntelligenceHub()
        self.readiness_gate = ReadinessGate()

    def register_skill(self, skill_name: str, skill_class: Type['BaseSkill']) -> None:
        """Helper to register a skill to the internal registry."""
        self.registry.register(skill_name, skill_class)

    async def handle_request(
        self, 
        student_id: str, 
        skill_name: str = None, 
        context: Dict[str, Any] = None, 
        schema: type[BaseModel] | None = None
    ) -> Any:
        """
        The core AI Reasoning Loop with Planner integration and Workflow Controller validation.
        
        1. Read Planner output for workflow guidance.
        2. Reason about the next goal.
        3. Execute skill via Pipeline Router (if available) or Registry (fallback).
        4. Validate next_action with Workflow Controller.
        5. Evaluate output.
        6. Update Planner with results.
        7. Return response.
        """
        logger.info(f"Career Coach handling request for student '{student_id}'")
        
        # Ensure student exists
        profile = self.memory.get_profile(student_id)
        if not profile:
            logger.warning(f"Student {student_id} not found. Creating default profile.")
            self.memory.create_student(student_id, "Unknown Student")
        
        # 1. Only call Planner if skill_name is not provided (genuine workflow decision needed)
        if skill_name:
            # Direct skill execution requested - skip Planner for efficiency
            target_skill = skill_name
            execution_plan = {'context': {}}
            logger.info(f"Direct skill execution requested: {target_skill} (skipping Planner)")
        else:
            # No skill specified - use Planner to determine next action
            execution_plan = await self.planner.build_execution_plan(student_id)
            logger.info(f"Planner execution plan: {execution_plan['current_stage']}")
            target_skill = execution_plan['next_skill']
        
        # Merge context with planner's context (if any)
        if context is None:
            context = {}
        context.update(execution_plan.get('context', {}))
        
        # Execute skill via Pipeline Router if available, else fallback to Registry
        if self.pipeline_router and self.pipeline_router.is_action_registered(target_skill):
            logger.info(f"Executing {target_skill} via PipelineRouter")
            result = await self.execute_via_pipeline(student_id, target_skill, context)
        else:
            logger.info(f"Executing {target_skill} via SkillRegistry (pipeline not registered)")
            result = await self.registry.execute(skill_name=target_skill, context=context, schema=schema, student_id=student_id)
        
        # 4. Validate next_action with Workflow Controller
        if hasattr(result, 'next_action'):
            current_state = workflow_controller.get_student_state(student_id)
            logger.info(f"Current workflow state: {current_state}")
            logger.info(f"Skill recommended next_action: {result.next_action}")
            
            # Mark current skill as completed
            from core.workflow_controller import Skill
            try:
                skill_enum = Skill(target_skill)
                workflow_controller.complete_skill(student_id, skill_enum)
            except ValueError:
                logger.warning(f"Skill {target_skill} not found in WorkflowController enum")
        
        # 5. Validation & Evaluation
        eval_data = result.model_dump() if hasattr(result, "model_dump") else {"raw_result": result}
        self.evaluation_engine.process(student_id=student_id, skill_name=target_skill, result=eval_data)
        
        # 6. Update Planner with skill completion
        updated_plan = await self.planner.update_plan_after_skill(student_id, target_skill, eval_data)
        
        # 7. Return response to API layer
        return result
    
    async def execute_via_pipeline(self, student_id: str, skill_name: str, context: Dict[str, Any]) -> Any:
        """
        Execute a skill via the Pipeline Router.
        
        Args:
            student_id: Student's unique identifier
            skill_name: Name of the skill to execute
            context: Additional context for execution
            
        Returns:
            PipelineResult from the pipeline execution
        """
        logger.info(f"CareerCoach: Executing {skill_name} via Pipeline Router for student {student_id}")
        
        # Get pipeline from router
        dependencies = {
            'llm': self.llm,
            'memory': self.memory,
            'career_intelligence': self.career_intelligence
        }
        pipeline = self.pipeline_router.get_pipeline(skill_name, dependencies)
        logger.info(f"CareerCoach: Pipeline obtained: {pipeline.__class__.__name__}")
        
        # Build pipeline context
        profile = self.memory.get_profile(student_id)
        pipeline_context = PipelineContext(
            student_id=student_id,
            current_module="preparation" if skill_name in ["survey", "assessment", "skill_gap", "roadmap", "learning", "reflection", "readiness"] else "placement",
            current_skill=skill_name,
            workflow_state=workflow_controller.get_student_state(student_id),
            student_memory=profile or {},
            career_intelligence=self.career_intelligence.get_student_intelligence(student_id) if self.career_intelligence else {},
            target_role=profile.get("target_role") if profile else None,
            skill_gaps=profile.get("skill_gaps", []) if profile else [],
            question_history=[],
            previous_result=None,
            additional_context=context
        )
        logger.info(f"CareerCoach: Pipeline context built for {skill_name}")
        
        # Execute pipeline
        logger.info(f"CareerCoach: Calling pipeline.execute() for {skill_name}")
        result = await pipeline.execute(pipeline_context)
        logger.info(f"CareerCoach: Pipeline execution completed for {skill_name}, result type: {type(result)}")
        
        return result
