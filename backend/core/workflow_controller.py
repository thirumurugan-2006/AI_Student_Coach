"""
Workflow Controller

Central authority for workflow state management and transition validation.

The Workflow Controller owns:
- current_module
- current_skill
- current_state
- completed_skills
- next_action
- allowed_transitions

Every transition must be validated by the Workflow Controller.
The LLM may recommend an action, but the Workflow Controller decides
whether the action is allowed based on the current state and workflow rules.
"""

from typing import Dict, Any, List, Optional, Set
from enum import Enum
from core.logger import logger


class Module(str, Enum):
    """Career preparation and placement modules."""
    CAREER_PREPARATION = "career_preparation"
    PLACEMENT_SIMULATION = "placement_simulation"


class Skill(str, Enum):
    """All available skills in the system."""
    # Career Preparation Module
    SURVEY = "survey"
    ASSESSMENT = "assessment"
    SKILL_GAP = "skill_gap"
    ROADMAP = "roadmap"
    LEARNING = "learning"
    REFLECTION = "reflection"
    READINESS = "readiness"
    
    # Placement Simulation Module
    PLACEMENT_APTITUDE = "placement_aptitude"
    PLACEMENT_CODING = "placement_coding"
    PLACEMENT_TECHNICAL = "placement_technical"
    PLACEMENT_INTERVIEW = "placement_interview"
    PLACEMENT_HR = "placement_hr"
    PLACEMENT_REPORT = "placement_report"
    
    # Dashboard
    DASHBOARD = "dashboard"


class WorkflowState(str, Enum):
    """Workflow states."""
    SIGNUP = "signup"
    SURVEY_IN_PROGRESS = "survey_in_progress"
    SURVEY_COMPLETED = "survey_completed"
    ASSESSMENT_IN_PROGRESS = "assessment_in_progress"
    ASSESSMENT_COMPLETED = "assessment_completed"
    SKILL_GAP_COMPLETED = "skill_gap_completed"
    ROADMAP_COMPLETED = "roadmap_completed"
    LEARNING_IN_PROGRESS = "learning_in_progress"
    LEARNING_COMPLETED = "learning_completed"
    REFLECTION_COMPLETED = "reflection_completed"
    READINESS_EVALUATED = "readiness_evaluated"
    PLACEMENT_IN_PROGRESS = "placement_in_progress"
    PLACEMENT_COMPLETED = "placement_completed"
    DASHBOARD = "dashboard"


class WorkflowController:
    """
    Central Workflow Controller for state management and transition validation.
    
    The Workflow Controller is the authoritative source for:
    - Current workflow state
    - Allowed transitions
    - Next action determination
    - Module progression
    
    The LLM (Qwen) may recommend actions, but the Workflow Controller
    validates whether those actions are allowed based on the current state.
    """
    
    # Define allowed transitions
    ALLOWED_TRANSITIONS: Dict[WorkflowState, Set[WorkflowState]] = {
        WorkflowState.SIGNUP: {
            WorkflowState.SURVEY_IN_PROGRESS,
        },
        WorkflowState.SURVEY_IN_PROGRESS: {
            WorkflowState.SURVEY_COMPLETED,
        },
        WorkflowState.SURVEY_COMPLETED: {
            WorkflowState.ASSESSMENT_IN_PROGRESS,
        },
        WorkflowState.ASSESSMENT_IN_PROGRESS: {
            WorkflowState.ASSESSMENT_COMPLETED,
        },
        WorkflowState.ASSESSMENT_COMPLETED: {
            WorkflowState.SKILL_GAP_COMPLETED,
        },
        WorkflowState.SKILL_GAP_COMPLETED: {
            WorkflowState.ROADMAP_COMPLETED,
        },
        WorkflowState.ROADMAP_COMPLETED: {
            WorkflowState.LEARNING_IN_PROGRESS,
        },
        WorkflowState.LEARNING_IN_PROGRESS: {
            WorkflowState.LEARNING_COMPLETED,
        },
        WorkflowState.LEARNING_COMPLETED: {
            WorkflowState.REFLECTION_COMPLETED,
        },
        WorkflowState.REFLECTION_COMPLETED: {
            WorkflowState.READINESS_EVALUATED,
        },
        WorkflowState.READINESS_EVALUATED: {
            WorkflowState.LEARNING_IN_PROGRESS,  # Not ready, continue learning
            WorkflowState.PLACEMENT_IN_PROGRESS,  # Ready, start placement
        },
        WorkflowState.PLACEMENT_IN_PROGRESS: {
            WorkflowState.PLACEMENT_COMPLETED,
        },
        WorkflowState.PLACEMENT_COMPLETED: {
            WorkflowState.DASHBOARD,
        },
        WorkflowState.DASHBOARD: {
            WorkflowState.LEARNING_IN_PROGRESS,
            WorkflowState.PLACEMENT_IN_PROGRESS,
        },
    }
    
    # Skill to state mapping
    SKILL_TO_STATE: Dict[Skill, WorkflowState] = {
        Skill.SURVEY: WorkflowState.SURVEY_IN_PROGRESS,
        Skill.ASSESSMENT: WorkflowState.ASSESSMENT_IN_PROGRESS,
        Skill.SKILL_GAP: WorkflowState.SKILL_GAP_COMPLETED,
        Skill.ROADMAP: WorkflowState.ROADMAP_COMPLETED,
        Skill.LEARNING: WorkflowState.LEARNING_IN_PROGRESS,
        Skill.REFLECTION: WorkflowState.REFLECTION_COMPLETED,
        Skill.READINESS: WorkflowState.READINESS_EVALUATED,
        Skill.PLACEMENT_APTITUDE: WorkflowState.PLACEMENT_IN_PROGRESS,
        Skill.PLACEMENT_CODING: WorkflowState.PLACEMENT_IN_PROGRESS,
        Skill.PLACEMENT_TECHNICAL: WorkflowState.PLACEMENT_IN_PROGRESS,
        Skill.PLACEMENT_INTERVIEW: WorkflowState.PLACEMENT_IN_PROGRESS,
        Skill.PLACEMENT_HR: WorkflowState.PLACEMENT_IN_PROGRESS,
        Skill.PLACEMENT_REPORT: WorkflowState.PLACEMENT_COMPLETED,
        Skill.DASHBOARD: WorkflowState.DASHBOARD,
    }
    
    # State to next skill mapping
    STATE_TO_NEXT_SKILL: Dict[WorkflowState, Skill] = {
        WorkflowState.SIGNUP: Skill.SURVEY,
        WorkflowState.SURVEY_COMPLETED: Skill.ASSESSMENT,
        WorkflowState.ASSESSMENT_COMPLETED: Skill.SKILL_GAP,
        WorkflowState.SKILL_GAP_COMPLETED: Skill.ROADMAP,
        WorkflowState.ROADMAP_COMPLETED: Skill.LEARNING,
        WorkflowState.LEARNING_COMPLETED: Skill.REFLECTION,
        WorkflowState.REFLECTION_COMPLETED: Skill.READINESS,
    }
    
    # Module to skills mapping
    MODULE_SKILLS: Dict[Module, List[Skill]] = {
        Module.CAREER_PREPARATION: [
            Skill.SURVEY,
            Skill.ASSESSMENT,
            Skill.SKILL_GAP,
            Skill.ROADMAP,
            Skill.LEARNING,
            Skill.REFLECTION,
            Skill.READINESS,
        ],
        Module.PLACEMENT_SIMULATION: [
            Skill.PLACEMENT_APTITUDE,
            Skill.PLACEMENT_CODING,
            Skill.PLACEMENT_TECHNICAL,
            Skill.PLACEMENT_INTERVIEW,
            Skill.PLACEMENT_HR,
            Skill.PLACEMENT_REPORT,
        ],
    }
    
    def __init__(self):
        """Initialize the Workflow Controller."""
        self.student_states: Dict[str, WorkflowState] = {}
        self.student_modules: Dict[str, Module] = {}
        self.student_completed_skills: Dict[str, Set[Skill]] = {}
        self.student_next_actions: Dict[str, Skill] = {}
    
    def get_student_state(self, student_id: str) -> WorkflowState:
        """
        Get the current workflow state for a student.
        
        Args:
            student_id: The student's ID
            
        Returns:
            Current workflow state
        """
        if student_id not in self.student_states:
            self.student_states[student_id] = WorkflowState.SIGNUP
            self.student_modules[student_id] = Module.CAREER_PREPARATION
            self.student_completed_skills[student_id] = set()
            logger.info(f"Initialized workflow state for student {student_id}: SIGNUP")
        
        return self.student_states[student_id]
    
    def get_student_module(self, student_id: str) -> Module:
        """
        Get the current module for a student.
        
        Args:
            student_id: The student's ID
            
        Returns:
            Current module
        """
        if student_id not in self.student_modules:
            self.student_modules[student_id] = Module.CAREER_PREPARATION
        
        return self.student_modules[student_id]
    
    def get_completed_skills(self, student_id: str) -> Set[Skill]:
        """
        Get the set of completed skills for a student.
        
        Args:
            student_id: The student's ID
            
        Returns:
            Set of completed skills
        """
        if student_id not in self.student_completed_skills:
            self.student_completed_skills[student_id] = set()
        
        return self.student_completed_skills[student_id]
    
    def validate_transition(
        self,
        student_id: str,
        from_state: WorkflowState,
        to_state: WorkflowState
    ) -> bool:
        """
        Validate if a transition is allowed.
        
        Args:
            student_id: The student's ID
            from_state: Current state
            to_state: Target state
            
        Returns:
            True if transition is allowed, False otherwise
        """
        current_state = self.get_student_state(student_id)
        
        if current_state != from_state:
            logger.warning(
                f"Transition validation failed for student {student_id}: "
                f"current state is {current_state}, but from_state is {from_state}"
            )
            return False
        
        if to_state not in self.ALLOWED_TRANSITIONS.get(from_state, set()):
            logger.warning(
                f"Transition validation failed for student {student_id}: "
                f"transition from {from_state} to {to_state} is not allowed"
            )
            return False
        
        logger.info(f"Transition validated for student {student_id}: {from_state} -> {to_state}")
        return True
    
    def transition_to(
        self,
        student_id: str,
        to_state: WorkflowState
    ) -> bool:
        """
        Transition a student to a new state.
        
        Args:
            student_id: The student's ID
            to_state: Target state
            
        Returns:
            True if transition was successful, False otherwise
        """
        current_state = self.get_student_state(student_id)
        
        if not self.validate_transition(student_id, current_state, to_state):
            return False
        
        self.student_states[student_id] = to_state
        logger.info(f"Transitioned student {student_id} to {to_state}")
        return True
    
    def complete_skill(
        self,
        student_id: str,
        skill: Skill
    ) -> bool:
        """
        Mark a skill as completed and transition to the next state.
        
        Args:
            student_id: The student's ID
            skill: The completed skill
            
        Returns:
            True if completion was successful, False otherwise
        """
        # Add to completed skills
        if student_id not in self.student_completed_skills:
            self.student_completed_skills[student_id] = set()
        
        self.student_completed_skills[student_id].add(skill)
        logger.info(f"Marked skill {skill} as completed for student {student_id}")
        
        # Determine next state based on skill
        target_state = self.SKILL_TO_STATE.get(skill)
        
        if target_state:
            return self.transition_to(student_id, target_state)
        
        return True
    
    def get_next_action(
        self,
        student_id: str,
        readiness_status: Optional[str] = None
    ) -> Skill:
        """
        Determine the next action for a student.
        
        Args:
            student_id: The student's ID
            readiness_status: Optional readiness status (ready, not_ready)
            
        Returns:
            Next skill to execute
        """
        current_state = self.get_student_state(student_id)
        current_module = self.get_student_module(student_id)
        
        # Special case: readiness evaluation determines next action
        if current_state == WorkflowState.READINESS_EVALUATED:
            if readiness_status == "ready":
                # Transition to placement module
                self.student_modules[student_id] = Module.PLACEMENT_SIMULATION
                self.student_states[student_id] = WorkflowState.PLACEMENT_IN_PROGRESS
                logger.info(f"Student {student_id} is ready, transitioning to Placement Simulation")
                return Skill.PLACEMENT_APTITUDE
            else:
                # Continue learning
                self.student_states[student_id] = WorkflowState.LEARNING_IN_PROGRESS
                logger.info(f"Student {student_id} not ready, continuing Learning")
                return Skill.LEARNING
        
        # Get next skill from state mapping
        next_skill = self.STATE_TO_NEXT_SKILL.get(current_state)
        
        if next_skill:
            return next_skill
        
        # Default to dashboard
        return Skill.DASHBOARD
    
    def get_placement_next_skill(
        self,
        student_id: str,
        completed_round: str
    ) -> Skill:
        """
        Determine the next placement skill based on completed round.
        
        Args:
            student_id: The student's ID
            completed_round: The just-completed placement round
            
        Returns:
            Next placement skill
        """
        placement_order = [
            Skill.PLACEMENT_APTITUDE,
            Skill.PLACEMENT_CODING,
            Skill.PLACEMENT_TECHNICAL,
            Skill.PLACEMENT_INTERVIEW,
            Skill.PLACEMENT_HR,
            Skill.PLACEMENT_REPORT,
        ]
        
        try:
            current_index = placement_order.index(Skill(completed_round))
            next_index = current_index + 1
            
            if next_index < len(placement_order):
                next_skill = placement_order[next_index]
                logger.info(f"Next placement skill for student {student_id}: {next_skill}")
                return next_skill
            else:
                # All placement rounds completed
                self.transition_to(student_id, WorkflowState.PLACEMENT_COMPLETED)
                return Skill.PLACEMENT_REPORT
        except (ValueError, IndexError):
            logger.warning(f"Invalid placement round {completed_round} for student {student_id}")
            return Skill.PLACEMENT_APTITUDE
    
    def reset_student(self, student_id: str) -> None:
        """
        Reset a student's workflow state (for testing purposes).
        
        Args:
            student_id: The student's ID
        """
        if student_id in self.student_states:
            del self.student_states[student_id]
        if student_id in self.student_modules:
            del self.student_modules[student_id]
        if student_id in self.student_completed_skills:
            del self.student_completed_skills[student_id]
        if student_id in self.student_next_actions:
            del self.student_next_actions[student_id]
        logger.info(f"Reset workflow state for student {student_id}")
    
    def get_workflow_summary(self, student_id: str) -> Dict[str, Any]:
        """
        Get a summary of the student's workflow state.
        
        Args:
            student_id: The student's ID
            
        Returns:
            Workflow summary dictionary
        """
        return {
            "student_id": student_id,
            "current_state": self.get_student_state(student_id),
            "current_module": self.get_student_module(student_id),
            "completed_skills": list(self.get_completed_skills(student_id)),
            "next_action": self.get_next_action(student_id),
        }


# Global workflow controller instance
workflow_controller = WorkflowController()
