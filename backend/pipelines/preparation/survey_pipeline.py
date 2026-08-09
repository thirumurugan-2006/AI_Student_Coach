"""
Survey Pipeline

Controls the execution of the Survey skill for career discovery.
Follows the standard Pipeline lifecycle.
"""

import uuid
from typing import Dict, Any
from pipelines.base_pipeline import BasePipeline
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult
from skills.survey.skill import SurveySkill
from skills.survey.schema import SurveyOutput
from services.question_service import QuestionService
from core.logger import logger


class SurveyPipeline(BasePipeline):
    """
    Pipeline for Survey skill execution.
    
    Responsible for:
    - Loading student context and survey instructions
    - Generating survey questions via Groq
    - Validating responses
    - Storing questions with backend-generated IDs
    - Checking for duplicates
    - Returning structured results
    """
    
    def __init__(self, llm=None, memory=None, career_intelligence=None):
        """Initialize SurveyPipeline with dependencies."""
        super().__init__(llm=llm, memory=memory, career_intelligence=career_intelligence)
        logger.info(f"SurveyPipeline: Initializing with llm={llm is not None}, memory={memory is not None}")
        self.question_service = QuestionService()
        self.survey_skill = SurveySkill(llm=llm, memory=memory)
        logger.info(f"SurveyPipeline: SurveySkill initialized")
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        """
        Execute the Survey Pipeline.
        
        Args:
            context: PipelineContext with student information
            
        Returns:
            PipelineResult with survey question
        """
        logger.info(f"SurveyPipeline: Starting execution for student {context.student_id}")
        
        try:
            # 1. Load workflow state
            context = await self.load_workflow_state(context)
            logger.info("SurveyPipeline: Step 1 - Workflow state loaded")
            
            # 2. Load student context
            context = await self.load_student_context(context)
            logger.info("SurveyPipeline: Step 2 - Student context loaded")
            
            # 3. Load career intelligence
            context = await self.load_career_intelligence(context)
            logger.info("SurveyPipeline: Step 3 - Career intelligence loaded")
            
            # 4. Load skill instructions
            instructions = await self.load_skill_instructions(context)
            logger.info("SurveyPipeline: Step 4 - Skill instructions loaded")
            
            # 5. Load previous activity
            context = await self.load_previous_activity(context)
            logger.info("SurveyPipeline: Step 5 - Previous activity loaded")
            
            # 6. Load question history for uniqueness
            context = await self.load_question_history(context)
            logger.info("SurveyPipeline: Step 6 - Question history loaded")
            
            # 7. Build execution context for skill
            skill_context = {
                "student_id": context.student_id,
                "current_message": context.additional_context.get("user_message", "Start survey"),
                "previous_questions": context.question_history
            }
            logger.info(f"SurveyPipeline: Step 7 - Skill context built: {skill_context}")
            
            # 8. Execute skill
            logger.info("SurveyPipeline: Step 8 - Executing SurveySkill")
            result = await self.survey_skill.execute(context=skill_context, schema=SurveyOutput)
            logger.info(f"SurveyPipeline: Step 8 - SurveySkill executed, result type: {type(result)}")
            
            # 9. Validate result
            if not await self.validate_result(result):
                logger.error("SurveyPipeline: Step 9 - Result validation failed")
                raise ValueError("Survey skill returned invalid result")
            logger.info("SurveyPipeline: Step 9 - Result validated")
            
            # 10. Extract result data - handle UniversalSkillOutput wrapper
            from core.skill_output import UniversalSkillOutput
            if isinstance(result, UniversalSkillOutput):
                result_dict = result.model_dump()
                survey_result = result_dict.get('result', {})
                logger.info("SurveyPipeline: Step 10 - Extracted from UniversalSkillOutput")
            elif hasattr(result, 'model_dump'):
                result_dict = result.model_dump()
                survey_result = result_dict
                logger.info("SurveyPipeline: Step 10 - Extracted from model_dump")
            else:
                survey_result = {"raw": str(result)}
                logger.info("SurveyPipeline: Step 10 - Extracted raw result")
            
            logger.info(f"SurveyPipeline: Step 10 - Survey result keys: {survey_result.keys() if isinstance(survey_result, dict) else 'not a dict'}")
            
            # 11. Evaluate result
            evaluation = await self.evaluate_result(context, result)
            logger.info("SurveyPipeline: Step 11 - Result evaluated")
            
            # 12. Create evidence
            evidence = []
            if survey_result.get('mcq_question'):
                evidence.append({
                    "type": "survey_question",
                    "question_id": survey_result['mcq_question'].get('question_id'),
                    "question_text": survey_result['mcq_question'].get('question'),
                    "timestamp": uuid.uuid4().hex
                })
            logger.info(f"SurveyPipeline: Step 12 - Evidence created: {len(evidence)} items")
            
            # 13. Update student memory
            await self.update_student_memory(context, result)
            logger.info("SurveyPipeline: Step 13 - Student memory updated")
            
            # 14. Update career intelligence
            await self.update_career_intelligence(context, result)
            logger.info("SurveyPipeline: Step 14 - Career intelligence updated")
            
            # 15. Determine next action
            next_action, next_action_reason = await self.determine_next_action(context, result)
            logger.info(f"SurveyPipeline: Step 15 - Next action: {next_action}")
            
            # 16. Calculate progress
            progress = 0.1  # Initial survey progress
            
            # 17. Create pipeline result
            pipeline_result = await self.create_pipeline_result(
                context=context,
                status="success",
                result=survey_result,
                evaluation=evaluation,
                evidence=evidence,
                progress=progress,
                next_action=next_action,
                next_action_reason=next_action_reason
            )
            
            logger.info(f"SurveyPipeline: Execution completed successfully")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"SurveyPipeline: Execution failed - {str(e)}", exc_info=True)
            return await self.create_pipeline_result(
                context=context,
                status="failed",
                result={},
                evaluation={},
                evidence=[],
                progress=0.0,
                next_action="survey",
                next_action_reason="Survey failed, retrying",
                error_message=str(e)
            )
    
    async def load_skill_instructions(self, context: PipelineContext) -> str:
        """Load survey instructions."""
        logger.info("SurveyPipeline: Loading survey instructions")
        # Instructions are loaded by the SurveySkill
        return ""
    
    async def load_question_history(self, context: PipelineContext) -> PipelineContext:
        """Load previous survey questions for uniqueness checking."""
        logger.info("SurveyPipeline: Loading question history")
        try:
            previous_questions = await self.question_service.get_previous_questions(
                student_id=context.student_id,
                skill="survey",
                limit=50
            )
            context.question_history = previous_questions
        except Exception as e:
            logger.warning(f"SurveyPipeline: Failed to load question history - {e}")
            context.question_history = []
        return context
    
    async def validate_result(self, result: Any) -> bool:
        """Validate survey result."""
        logger.debug("SurveyPipeline: Validating result")
        if result is None:
            return False
        
        # Check if result has expected structure
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            return 'result' in result_dict
        
        return True
    
    async def evaluate_result(self, context: PipelineContext, result: Any) -> Dict[str, Any]:
        """Evaluate survey result."""
        logger.info("SurveyPipeline: Evaluating result")
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        survey_result = result_dict.get('result', {})
        
        return {
            "survey_completed": survey_result.get('survey_completed', False),
            "question_generated": bool(survey_result.get('mcq_question')),
            "profile_updated": True
        }
    
    async def determine_next_action(self, context: PipelineContext, result: Any) -> tuple[str, str]:
        """Determine next action based on survey completion."""
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else {"raw": str(result)}
        survey_result = result_dict.get('result', {})
        survey_completed = survey_result.get('survey_completed', False)
        
        if survey_completed:
            return "assessment", "Survey completed, moving to assessment"
        else:
            return "survey", "Continue survey to collect more information"
