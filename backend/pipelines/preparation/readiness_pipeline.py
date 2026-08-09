"""
Readiness Pipeline

Evaluates student readiness for placement simulation.
Calculates readiness score based on evidence, NOT LLM-generated scores.
"""

from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from core.logger import logger


def _roadmap_topic_count(student_memory: dict) -> int:
    roadmap = student_memory.get("roadmap", [])
    if isinstance(roadmap, dict):
        return len(roadmap.get("topics", []))
    if isinstance(roadmap, list):
        return len(roadmap)
    return 0


class ReadinessPipeline(BasePipeline):
    """
    Pipeline for Readiness evaluation.
    
    Responsible for:
    - Loading assessment evidence
    - Loading learning progress
    - Loading skill mastery data
    - Loading confidence metrics
    - Loading skill gaps
    - Calculating readiness score (NOT LLM-generated)
    - Returning structured readiness evaluation
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize ReadinessPipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Readiness Pipeline.
        
        Args:
            context: PipelineContext with student information
            
        Returns:
            PipelineResult with readiness evaluation
        """
        logger.info(f"ReadinessPipeline: Starting execution for student {context.student_id}")
        
        try:
            # 1. Load workflow state
            context = await self.load_workflow_state(context)
            
            # 2. Load student context
            context = await self.load_student_context(context)
            
            # 3. Load career intelligence
            context = await self.load_career_intelligence(context)
            
            # 4. Load previous activity
            context = await self.load_previous_activity(context)
            
            # 5. Calculate readiness metrics (NOT LLM-generated)
            logger.info("ReadinessPipeline: Calculating readiness metrics")
            readiness_metrics = await self.calculate_readiness_metrics(context)
            
            # 6. Determine overall readiness
            overall_readiness = readiness_metrics["overall_readiness"]
            status = "ready" if overall_readiness >= 70 else "not_ready"
            
            # 7. Create readiness result
            readiness_result = {
                "technical_readiness": readiness_metrics["technical_readiness"],
                "learning_progress": readiness_metrics["learning_progress"],
                "skill_mastery": readiness_metrics["skill_mastery"],
                "confidence": readiness_metrics["confidence"],
                "overall_readiness": overall_readiness,
                "status": status,
                "strengths": readiness_metrics["strengths"],
                "weaknesses": readiness_metrics["weaknesses"],
                "recommendations": readiness_metrics["recommendations"]
            }
            
            # 8. Evaluate result
            evaluation = await self.evaluate_result(context, readiness_result)
            
            # 9. Create evidence
            evidence = [{
                "type": "readiness_evaluation",
                "overall_readiness": overall_readiness,
                "status": status,
                "timestamp": context.additional_context.get("timestamp", "")
            }]
            
            # 10. Update student memory
            await self.update_student_memory(context, readiness_result)
            
            # 11. Update career intelligence
            await self.update_career_intelligence(context, readiness_result)
            
            # 12. Determine next action
            next_action, next_action_reason = await self.determine_next_action(context, readiness_result)
            
            # 13. Calculate progress
            progress = 0.75  # Readiness progress
            
            # 14. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result=readiness_result,
                evaluation=evaluation,
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"ReadinessPipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"ReadinessPipeline: Execution failed - {str(e)}")
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="readiness",
                next_action_reason="Readiness evaluation failed, retrying",
                error_message=str(e)
            )
    
    async def calculate_readiness_metrics(self, context: PipelineContext) -> Dict[str, Any]:
        """Calculate readiness metrics from actual evidence."""
        logger.info("ReadinessPipeline: Calculating readiness metrics from evidence")
        
        # Get assessment performance
        assessment_perf = context.student_memory.get("assessment_performance", {})
        technical_readiness = assessment_perf.get("accuracy", 0)
        
        # Get learning progress
        completed_topics = len(context.student_memory.get("completed_topics", []))
        total_topics = _roadmap_topic_count(context.student_memory)
        learning_progress = (completed_topics / total_topics * 100) if total_topics > 0 else 0
        
        # Get skill mastery (inverse of skill gaps)
        skill_gaps = context.student_memory.get("skill_gaps", [])
        skill_mastery = max(0, 100 - len(skill_gaps) * 10)  # Simple heuristic
        
        # Get confidence from reflections
        reflection_notes = context.student_memory.get("reflection_notes", [])
        confidence = 70 if reflection_notes else 50  # Default confidence
        
        # Calculate overall readiness
        overall_readiness = (technical_readiness + learning_progress + skill_mastery + confidence) / 4
        
        # Determine strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if technical_readiness >= 70:
            strengths.append("Strong technical skills")
        else:
            weaknesses.append("Technical skills need improvement")
        
        if learning_progress >= 70:
            strengths.append("Good learning progress")
        else:
            weaknesses.append("Learning progress needs improvement")
        
        if skill_mastery >= 70:
            strengths.append("Good skill mastery")
        else:
            weaknesses.append("Skill mastery needs improvement")
        
        # Generate recommendations
        recommendations = []
        if overall_readiness < 70:
            recommendations.append("Continue learning to improve skill gaps")
            recommendations.append("Practice more assessment questions")
        else:
            recommendations.append("Ready for placement simulation")
        
        return {
            "technical_readiness": round(technical_readiness, 2),
            "learning_progress": round(learning_progress, 2),
            "skill_mastery": round(skill_mastery, 2),
            "confidence": round(confidence, 2),
            "overall_readiness": round(overall_readiness, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations
        }
    
    async def evaluate_result(self, context: PipelineContext, result: Any) -> Dict[str, Any]:
        """Evaluate readiness result."""
        logger.info("ReadinessPipeline: Evaluating result")
        return {
            "overall_readiness": result.get("overall_readiness", 0),
            "status": result.get("status", "not_ready"),
            "strengths_count": len(result.get("strengths", [])),
            "weaknesses_count": len(result.get("weaknesses", []))
        }
    
    async def update_student_memory(self, context: PipelineContext, result: Any) -> bool:
        """Update student memory with readiness evaluation."""
        logger.info("ReadinessPipeline: Updating student memory")
        if self.memory and context.student_id:
            profile = context.student_memory or self.memory.get_profile(context.student_id)
            if profile:
                profile["readiness_evaluation"] = result
                profile["readiness_evaluated"] = True
                profile["readiness_score"] = result.get("overall_readiness", 0)
                
                context.student_memory = profile
                await self.persist_memory(context)
        return True
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action based on readiness status."""
        status = result.get("status", "not_ready")
        
        if status == "ready":
            return "placement_aptitude", "Ready for placement simulation, starting with aptitude test"
        else:
            return "learning", "Not ready for placement, continue learning to improve skills"
