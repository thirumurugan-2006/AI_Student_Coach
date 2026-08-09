"""
Planner Agent

Responsible for workflow orchestration and execution planning using Qwen 4B.

The Planner:
- Reads Student Memory
- Reads Current Session
- Reads Career Goal
- Reads Progress
- Reads Evaluation Results
- Uses Qwen 4B for reasoning about next actions
- Determines the current stage
- Builds an execution plan

The Planner never executes Skills.
The Planner only creates the execution plan.
The Workflow Controller validates transitions.
"""

from typing import Dict, Any, List, Optional
from core.logger import logger
from core.llm_interface import LLMInterface


class Planner:
    """
    Planner Agent for workflow orchestration using Qwen 4B for reasoning.
    
    Determines the next step in the student's career coaching journey
    based on their current state, progress, and evaluation results.
    Uses Qwen 4B for intelligent reasoning about next actions.
    """
    
    def __init__(self, memory, llm: Optional[LLMInterface] = None):
        """
        Initialize the Planner with Student Memory and optional LLM.
        
        Args:
            memory: StudentMemory instance
            llm: Optional LLMInterface for Qwen-based planning
        """
        self.memory = memory
        self.llm = llm
        self.workflow_stages = [
            "survey",
            "assessment",
            "skill_gap",
            "roadmap",
            "learning",
            "reflection",
            "readiness",
            "placement_aptitude",
            "placement_coding",
            "placement_technical",
            "placement_interview",
            "placement_hr",
            "placement_report",
            "dashboard"
        ]
    
    def determine_current_stage(self, student_id: str) -> str:
        """
        Determine the current stage of the student's journey.
        
        Args:
            student_id: The student's ID
            
        Returns:
            Current stage name
        """
        profile = self.memory.get_profile(student_id)
        
        if not profile:
            logger.warning(f"No profile found for student {student_id}")
            return "survey"
        
        # Check survey completion
        if not profile.get("survey_completed", False):
            return "survey"
        
        # Check assessment completion
        if not profile.get("assessment_completed", False):
            return "assessment"
        
        # Check skill gap completion
        if not profile.get("skill_gap_completed", False):
            return "skill_gap"
        
        # Check roadmap completion
        roadmap = profile.get("roadmap", [])
        if not roadmap:
            return "roadmap"
        
        # Check learning progress
        completed = profile.get("completed_topics", [])
        if roadmap and len(completed) < len(roadmap):
            return "learning"
        
        # Check reflection completion
        reflection_count = len(profile.get("reflection_notes", []))
        if reflection_count == 0:
            return "reflection"
        
        # Check readiness evaluation
        if not profile.get("readiness_evaluated", False):
            return "readiness"
        
        # Check placement completion
        if not profile.get("placement_completed", False):
            # Determine which placement round
            placement_rounds = profile.get("placement_rounds_completed", [])
            if "aptitude" not in placement_rounds:
                return "placement_aptitude"
            elif "coding" not in placement_rounds:
                return "placement_coding"
            elif "technical" not in placement_rounds:
                return "placement_technical"
            elif "interview" not in placement_rounds:
                return "placement_interview"
            elif "hr" not in placement_rounds:
                return "placement_hr"
            else:
                return "placement_report"
        
        # Default to dashboard
        return "dashboard"
    
    async def build_execution_plan(self, student_id: str) -> Dict[str, Any]:
        """
        Build an execution plan for the student using Qwen for reasoning if available.
        
        Args:
            student_id: The student's ID
            
        Returns:
            Execution plan dictionary
        """
        profile = self.memory.get_profile(student_id)
        current_stage = self.determine_current_stage(student_id)
        
        # Use Qwen for intelligent reasoning if available
        if self.llm:
            try:
                reasoning = await self._generate_llm_reasoning(student_id, current_stage, profile)
            except Exception as e:
                logger.warning(f"LLM reasoning failed for student {student_id}: {e}")
                reasoning = self._generate_rule_based_reasoning(student_id, current_stage)
        else:
            reasoning = self._generate_rule_based_reasoning(student_id, current_stage)
        
        plan = {
            "student_id": student_id,
            "current_stage": current_stage,
            "next_skill": current_stage,
            "context": self._build_context(student_id, current_stage),
            "reasoning": reasoning,
            "estimated_completion": self._estimate_completion(student_id)
        }
        
        logger.info(f"Planner built execution plan for student {student_id}: {current_stage}")
        return plan
    
    async def _generate_llm_reasoning(
        self,
        student_id: str,
        current_stage: str,
        profile: Dict[str, Any]
    ) -> str:
        """
        Use Qwen 4B to generate intelligent reasoning about the next action.
        
        Args:
            student_id: The student's ID
            current_stage: Current workflow stage
            profile: Student profile
            
        Returns:
            Reasoning string from Qwen
        """
        prompt = f"""
You are an AI Career Coach Planner. Analyze the student's current state and provide reasoning for the next action.

Student ID: {student_id}
Current Stage: {current_stage}

Student Profile:
- Career Goal: {profile.get('career_goal', 'Not specified')}
- Experience Level: {profile.get('experience_level', 'Not specified')}
- Target Role: {profile.get('target_role', 'Not specified')}
- Skills: {profile.get('skills', {})}
- Skill Gaps: {profile.get('skill_gaps', [])}
- Readiness Score: {profile.get('readiness_score', 0)}
- Learning Progress: {profile.get('learning_progress', 0)}

Completed Stages:
- Survey: {profile.get('survey_completed', False)}
- Assessment: {profile.get('assessment_completed', False)}
- Skill Gap: {profile.get('skill_gap_completed', False)}
- Roadmap: {profile.get('roadmap_completed', False)}
- Learning: {profile.get('learning_completed', False)}
- Reflection: {profile.get('reflection_completed', False)}
- Readiness: {profile.get('readiness_evaluated', False)}
- Placement: {profile.get('placement_completed', False)}

Provide a brief reasoning (1-2 sentences) for why the student should proceed to the {current_stage} stage.
Focus on the student's progress, gaps, and readiness.
"""
        
        try:
            reasoning = await self.llm.generate(prompt=prompt, use_planning=True)
            return str(reasoning) if reasoning else self._generate_rule_based_reasoning(student_id, current_stage)
        except Exception as e:
            logger.warning(f"LLM reasoning failed: {e}")
            return self._generate_rule_based_reasoning(student_id, current_stage)
    
    def _generate_rule_based_reasoning(self, student_id: str, stage: str) -> str:
        """
        Generate rule-based reasoning as fallback.
        
        Args:
            student_id: The student's ID
            stage: Current stage
            
        Returns:
            Reasoning string
        """
        reasoning_map = {
            "survey": "Survey not completed. Need to collect student profile information.",
            "assessment": "Survey completed. Need to assess current skill levels.",
            "skill_gap": "Assessment completed. Need to identify skill gaps.",
            "roadmap": "Skill gaps identified. Need to create personalized learning roadmap.",
            "learning": "Roadmap created. Need to follow learning modules to build skills.",
            "reflection": "Learning in progress. Need to reflect on performance and insights.",
            "readiness": "Reflection completed. Need to evaluate readiness for placement simulation.",
            "placement_aptitude": "Ready for placement. Starting with aptitude test.",
            "placement_coding": "Aptitude completed. Moving to coding round.",
            "placement_technical": "Coding completed. Moving to technical interview.",
            "placement_interview": "Technical completed. Moving to behavioral interview.",
            "placement_hr": "Interview completed. Moving to HR round.",
            "placement_report": "All placement rounds completed. Generating placement report.",
            "dashboard": "All stages completed. Showing comprehensive dashboard."
        }
        
        return reasoning_map.get(stage, "Unknown stage")
    
    def _build_context(self, student_id: str, stage: str) -> Dict[str, Any]:
        """
        Build context for the current stage.
        
        Args:
            student_id: The student's ID
            stage: Current stage
            
        Returns:
            Context dictionary
        """
        profile = self.memory.get_profile(student_id)
        
        context = {
            "student_id": student_id,
            "stage": stage,
            "career_goal": profile.get("career_goal", "Not specified"),
            "experience_level": profile.get("experience_level", "Not specified"),
            "readiness_score": profile.get("readiness_score", 0)
        }
        
        # Add stage-specific context
        if stage == "survey":
            context["survey_status"] = profile.get("survey_completed", False)
        elif stage == "assessment":
            context["assessment_history"] = profile.get("assessment_history", [])
        elif stage in ["skill_gap", "roadmap"]:
            context["skills"] = profile.get("skills", {})
            context["skill_gaps"] = profile.get("skill_gaps", [])
        elif stage == "learning":
            context["roadmap"] = profile.get("roadmap", [])
            context["completed_topics"] = profile.get("completed_topics", [])
        elif stage == "reflection":
            context["reflection_notes"] = profile.get("reflection_notes", [])
        elif stage == "readiness":
            context["learning_progress"] = profile.get("learning_progress", 0)
            context["assessment_scores"] = profile.get("assessment_scores", {})
        elif stage.startswith("placement_"):
            context["placement_rounds_completed"] = profile.get("placement_rounds_completed", [])
            context["placement_scores"] = profile.get("placement_scores", {})
        elif stage == "dashboard":
            context["full_profile"] = profile
        
        return context
    
    def _estimate_completion(self, student_id: str) -> Dict[str, Any]:
        """
        Estimate completion status for the student's journey.
        
        Args:
            student_id: The student's ID
            
        Returns:
            Completion estimate dictionary
        """
        profile = self.memory.get_profile(student_id)
        
        completed_stages = []
        if profile.get("survey_completed", False):
            completed_stages.append("survey")
        if profile.get("assessment_completed", False):
            completed_stages.append("assessment")
        if profile.get("skill_gap_completed", False):
            completed_stages.append("skill_gap")
        if profile.get("roadmap_completed", False):
            completed_stages.append("roadmap")
        if profile.get("learning_completed", False):
            completed_stages.append("learning")
        if profile.get("reflection_completed", False):
            completed_stages.append("reflection")
        if profile.get("readiness_evaluated", False):
            completed_stages.append("readiness")
        if profile.get("placement_completed", False):
            completed_stages.append("placement")
        
        total_stages = len(self.workflow_stages)
        completed_count = len(completed_stages)
        completion_percentage = (completed_count / total_stages) * 100
        
        return {
            "total_stages": total_stages,
            "completed_stages": completed_stages,
            "completion_percentage": round(completion_percentage, 2)
        }
    
    async def update_plan_after_skill(self, student_id: str, skill_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the execution plan after a skill completes.
        
        Args:
            student_id: The student's ID
            skill_name: Name of the completed skill
            result: Result from the skill execution
            
        Returns:
            Updated execution plan
        """
        logger.info(f"Planner updating plan after {skill_name} completion for student {student_id}")
        
        # Rebuild plan with updated memory
        return await self.build_execution_plan(student_id)
