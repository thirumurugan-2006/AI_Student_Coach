"""
Skill Gap Pipeline

Analyzes student skills and identifies gaps.
Uses assessment and survey evidence to create skill gap analysis.
"""

from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from skills.skill_gap.skill import SkillGapSkill
from skills.skill_gap.schema import SkillGapOutput
from core.logger import logger


class SkillGapPipeline(BasePipeline):
    """
    Pipeline for Skill Gap analysis.
    
    Responsible for:
    - Loading survey and assessment evidence
    - Loading target role and career goal
    - Loading existing skills
    - Analyzing skill gaps via Groq
    - Creating strong_skills, weak_skills, skill_gaps
    - Storing career intelligence
    - Returning structured results
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize SkillGapPipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
        self.skill_gap_skill = SkillGapSkill(llm=llm, memory=memory)
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Skill Gap Pipeline.
        
        Args:
            context: PipelineContext with student information
            
        Returns:
            PipelineResult with skill gap analysis
        """
        logger.info(f"SkillGapPipeline: Starting execution for student {context.student_id}")
        
        try:
            # 1. Load workflow state
            context = await self.load_workflow_state(context)
            
            # 2. Load student context
            context = await self.load_student_context(context)
            
            # 3. Load career intelligence
            context = await self.load_career_intelligence(context)
            
            # 4. Load previous activity
            context = await self.load_previous_activity(context)
            
            # 5. Build execution context for skill
            skill_context = {
                "student_id": context.student_id,
                "target_role": context.target_role or context.student_memory.get("target_role", "Software Engineer"),
                "career_goal": context.student_memory.get("career_goal", ""),
                "existing_skills": context.student_memory.get("skills", {}),
                "assessment_performance": context.student_memory.get("assessment_performance", {}),
                "survey_answers": context.student_memory.get("survey_answers", {})
            }
            
            # 6. Execute skill
            logger.info("SkillGapPipeline: Executing SkillGapSkill")
            result = await self.skill_gap_skill.execute(context=skill_context, schema=SkillGapOutput)
            
            # 7. Validate result
            if not await self.validate_result(result):
                raise ValueError("SkillGap skill returned invalid result")
            
            # 8. Extract result data
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
            skill_gap_result = result_dict.get('result', {})
            
            # 9. Evaluate result
            evaluation = await self.evaluate_result(context, result)
            
            # 10. Create evidence
            evidence = [{
                "type": "skill_gap_analysis",
                "strong_skills": skill_gap_result.get('strong_skills', []),
                "weak_skills": skill_gap_result.get('weak_skills', []),
                "skill_gaps": skill_gap_result.get('skill_gaps', []),
                "timestamp": context.additional_context.get("timestamp", "")
            }]
            
            # 11. Update student memory
            await self.update_student_memory(context, result)
            
            # 12. Update career intelligence
            await self.update_career_intelligence(context, result)
            
            # 13. Determine next action
            next_action, next_action_reason = await self.determine_next_action(context, result)
            
            # 14. Calculate progress
            progress = 0.35  # Skill gap progress
            
            # 15. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result=skill_gap_result,
                evaluation=evaluation,
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"SkillGapPipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"SkillGapPipeline: Execution failed - {str(e)}")
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="skill_gap",
                next_action_reason="Skill gap analysis failed, retrying",
                error_message=str(e)
            )
    
    async def validate_result(self, result: Any) -> bool:
        """Validate skill gap result."""
        logger.debug("SkillGapPipeline: Validating result")
        if result is None:
            return False
        
        # Check if result has expected structure
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return 'result' in result_dict
        
        return True
    
    async def evaluate_result(self, context: PipelineContext, result: Any) -> Dict[str, Any]:
        """Evaluate skill gap result."""
        logger.info("SkillGapPipeline: Evaluating result")
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        skill_gap_result = result_dict.get('result', {})
        
        return {
            "strong_skills_count": len(skill_gap_result.get('strong_skills', [])),
            "weak_skills_count": len(skill_gap_result.get('weak_skills', [])),
            "skill_gaps_count": len(skill_gap_result.get('skill_gaps', [])),
            "priority_count": len(skill_gap_result.get('priority', []))
        }
    
    async def update_student_memory(self, context: PipelineContext, result: Any) -> bool:
        """Update student memory with skill gap analysis."""
        logger.info("SkillGapPipeline: Updating student memory")
        if self.memory and context.student_id:
            profile = context.student_memory or self.memory.get_profile(context.student_id)
            if profile:
                result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
                skill_gap_result = result_dict.get('result', {})
                
                profile["skill_gaps"] = skill_gap_result.get('skill_gaps', [])
                profile["strong_skills"] = skill_gap_result.get('strong_skills', [])
                profile["weak_skills"] = skill_gap_result.get('weak_skills', [])
                profile["skill_gap_completed"] = True
                
                context.student_memory = profile
                await self.persist_memory(context)
        return True
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action after skill gap analysis."""
        return "roadmap", "Skill gap analysis completed, generating personalized roadmap"
