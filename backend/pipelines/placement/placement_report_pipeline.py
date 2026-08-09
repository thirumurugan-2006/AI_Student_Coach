"""
Placement Report Pipeline

Generates comprehensive placement report based on all placement evidence.
Calculates scores from actual evidence, NOT LLM-generated values.
"""

from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from services.question_service import QuestionService
from core.logger import logger


class PlacementReportPipeline(BasePipeline):
    """
    Pipeline for Placement Report generation.
    
    Responsible for:
    - Loading all placement evidence
    - Calculating aptitude_score from actual attempts
    - Calculating coding_score from actual attempts
    - Calculating technical_score from actual attempts
    - Calculating communication_score from actual attempts
    - Calculating interview_score from actual attempts
    - Calculating hr_score from actual attempts
    - Calculating confidence from actual evidence
    - Calculating overall_placement_readiness
    - Identifying strengths and skill gaps
    - Generating recommendations
    - Returning structured placement report
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize PlacementReportPipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
        self.question_service = QuestionService()
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Placement Report Pipeline.
        
        Args:
            context: PipelineContext with student information
            
        Returns:
            PipelineResult with placement report
        """
        logger.info(f"PlacementReportPipeline: Starting execution for student {context.student_id}")
        
        try:
            # 1. Load workflow state
            context = await self.load_workflow_state(context)
            
            # 2. Load student context
            context = await self.load_student_context(context)
            
            # 3. Load career intelligence
            context = await self.load_career_intelligence(context)
            
            # 4. Load previous activity
            context = await self.load_previous_activity(context)
            
            # 5. Calculate placement scores from actual evidence
            logger.info("PlacementReportPipeline: Calculating placement scores from evidence")
            placement_scores = await self.calculate_placement_scores(context)
            
            # 6. Generate placement report
            placement_report = {
                "target_role": context.target_role or context.student_memory.get("target_role", "Software Engineer"),
                "aptitude_score": placement_scores["aptitude_score"],
                "coding_score": placement_scores["coding_score"],
                "technical_score": placement_scores["technical_score"],
                "communication_score": placement_scores["communication_score"],
                "interview_score": placement_scores["interview_score"],
                "hr_score": placement_scores["hr_score"],
                "confidence": placement_scores["confidence"],
                "overall_placement_readiness": placement_scores["overall_placement_readiness"],
                "strengths": placement_scores["strengths"],
                "skill_gaps": placement_scores["skill_gaps"],
                "recommendations": placement_scores["recommendations"]
            }
            
            # 7. Evaluate result
            evaluation = await self.evaluate_result(context, placement_report)
            
            # 8. Create evidence
            evidence = [{
                "type": "placement_report",
                "overall_placement_readiness": placement_report["overall_placement_readiness"],
                "timestamp": context.additional_context.get("timestamp", "")
            }]
            
            # 9. Update student memory
            await self.update_student_memory(context, placement_report)
            
            # 10. Update career intelligence
            await self.update_career_intelligence(context, placement_report)
            
            # 11. Determine next action
            next_action, next_action_reason = await self.determine_next_action(context, placement_report)
            
            # 12. Calculate progress
            progress = 1.0  # Placement complete
            
            # 13. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result=placement_report,
                evaluation=evaluation,
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"PlacementReportPipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"PlacementReportPipeline: Execution failed - {str(e)}")
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="placement_report",
                next_action_reason="Placement report generation failed, retrying",
                error_message=str(e)
            )
    
    async def calculate_placement_scores(self, context: PipelineContext) -> Dict[str, Any]:
        """Calculate placement scores from actual evidence."""
        logger.info("PlacementReportPipeline: Calculating scores from actual evidence")
        
        # Calculate scores from actual attempts
        aptitude_score = await self.calculate_skill_score(context.student_id, "placement_aptitude")
        coding_score = await self.calculate_skill_score(context.student_id, "placement_coding")
        technical_score = await self.calculate_skill_score(context.student_id, "placement_technical")
        interview_score = await self.calculate_skill_score(context.student_id, "placement_interview")
        hr_score = await self.calculate_skill_score(context.student_id, "placement_hr")
        
        # Communication score (average of interview and HR)
        communication_score = (interview_score + hr_score) / 2
        
        # Confidence from readiness evaluation
        confidence = context.student_memory.get("readiness_evaluation", {}).get("confidence", 70)
        
        # Overall placement readiness (weighted average)
        overall_placement_readiness = (
            aptitude_score * 0.15 +
            coding_score * 0.25 +
            technical_score * 0.25 +
            communication_score * 0.15 +
            confidence * 0.20
        )
        
        # Identify strengths
        strengths = []
        if aptitude_score >= 70:
            strengths.append("Strong aptitude skills")
        if coding_score >= 70:
            strengths.append("Strong coding skills")
        if technical_score >= 70:
            strengths.append("Strong technical knowledge")
        if communication_score >= 70:
            strengths.append("Good communication skills")
        
        # Identify skill gaps
        skill_gaps = []
        if aptitude_score < 60:
            skill_gaps.append("Aptitude needs improvement")
        if coding_score < 60:
            skill_gaps.append("Coding skills need improvement")
        if technical_score < 60:
            skill_gaps.append("Technical knowledge needs improvement")
        if communication_score < 60:
            skill_gaps.append("Communication skills need improvement")
        
        # Generate recommendations
        recommendations = []
        if overall_placement_readiness >= 75:
            recommendations.append("Ready for placement interviews")
            recommendations.append("Focus on interview preparation")
        elif overall_placement_readiness >= 60:
            recommendations.append("Good progress, continue practicing")
            recommendations.append("Focus on weak areas")
        else:
            recommendations.append("Need more preparation")
            recommendations.append("Focus on learning and practice")
        
        return {
            "aptitude_score": round(aptitude_score, 2),
            "coding_score": round(coding_score, 2),
            "technical_score": round(technical_score, 2),
            "communication_score": round(communication_score, 2),
            "interview_score": round(interview_score, 2),
            "hr_score": round(hr_score, 2),
            "confidence": round(confidence, 2),
            "overall_placement_readiness": round(overall_placement_readiness, 2),
            "strengths": strengths,
            "skill_gaps": skill_gaps,
            "recommendations": recommendations
        }
    
    async def calculate_skill_score(self, student_id: str, skill: str) -> float:
        """Calculate skill score from actual attempts."""
        logger.info(f"PlacementReportPipeline: Calculating score for {skill}")
        try:
            attempts = await self.question_service.get_student_attempts(
                student_id=student_id,
                skill=skill
            )
            
            if not attempts:
                return 0.0
            
            correct_answers = sum(1 for attempt in attempts if attempt.get("is_correct"))
            total_attempts = len(attempts)
            
            return (correct_answers / total_attempts * 100) if total_attempts > 0 else 0.0
        except Exception as e:
            logger.warning(f"PlacementReportPipeline: Failed to calculate score for {skill} - {e}")
            return 0.0
    
    async def evaluate_result(self, context: PipelineContext, result: Any) -> Dict[str, Any]:
        """Evaluate placement report result."""
        logger.info("PlacementReportPipeline: Evaluating result")
        return {
            "overall_placement_readiness": result.get("overall_placement_readiness", 0),
            "strengths_count": len(result.get("strengths", [])),
            "skill_gaps_count": len(result.get("skill_gaps", [])),
            "recommendations_count": len(result.get("recommendations", []))
        }
    
    async def update_student_memory(self, context: PipelineContext, result: Any) -> bool:
        """Update student memory with placement report."""
        logger.info("PlacementReportPipeline: Updating student memory")
        if self.memory and context.student_id:
            profile = context.student_memory or self.memory.get_profile(context.student_id)
            if profile:
                profile["placement_report"] = result
                profile["placement_completed"] = True
                
                context.student_memory = profile
                await self.persist_memory(context)
        return True
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action after placement report."""
        overall_readiness = result.get("overall_placement_readiness", 0)
        
        if overall_readiness >= 75:
            return "dashboard", "Placement simulation complete, ready for interviews"
        else:
            return "learning", "Placement simulation complete, continue learning to improve skills"
