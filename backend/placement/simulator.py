"""
Placement Simulator

Controls the placement simulation workflow.
The LLM must NOT decide the workflow — the backend does.
"""

from typing import Dict, Any, Optional
from core.logger import logger

from placement.planner import PlacementPlanner
from placement.evaluator.evaluator import PlacementEvaluator
from placement.report.generator import PlacementReportGenerator
from memory.student_memory import StudentMemory


class PlacementSimulator:
    """
    Controls the placement simulation workflow.

    Flow:
    Readiness Gate
        ↓
    Placement Planner
        ↓
    Aptitude
        ↓
    Evaluation
        ↓
    Coding
        ↓
    Evaluation
        ↓
    Technical
        ↓
    Evaluation
        ↓
    Interview
        ↓
    Evaluation
        ↓
    HR
        ↓
    Evaluation
        ↓
    Final Placement Score
        ↓
    Recruiter Report
        ↓
    Career Intelligence
        ↓
    Updated Skill Gap
        ↓
    Next Best Action
    """

    ROUNDS = [
        "aptitude",
        "coding",
        "technical",
        "interview",
        "hr"
    ]

    def __init__(self, memory: StudentMemory, llm, evaluator: PlacementEvaluator = None):
        self.memory = memory
        self.llm = llm
        self.planner = PlacementPlanner(memory)
        self.evaluator = evaluator or PlacementEvaluator(memory)
        self.report_generator = PlacementReportGenerator(memory, llm)

    async def start_simulation(self, student_id: str) -> Dict[str, Any]:
        """
        Start a new placement simulation for a student.

        Returns:
            Simulation state with first round
        """
        logger.info(f"Starting placement simulation for student {student_id}")

        # Check readiness
        readiness = self._check_readiness(student_id)
        if not readiness["ready"]:
            return {
                "status": "blocked",
                "reason": readiness["reason"]
            }

        plan = self.planner.build_execution_plan(student_id)
        first_round = plan["next_round"]

        simulation_state = {
            "student_id": student_id,
            "status": "started",
            "current_round": first_round,
            "rounds_completed": [],
            "round_results": {},
            "overall_score": 0.0
        }

        logger.info(f"Placement simulation started for student {student_id}")
        return simulation_state

    async def execute_round(self, student_id: str, round_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a specific placement round.

        Args:
            student_id: The student's ID
            round_type: One of: aptitude, coding, technical, interview, hr
            context: Optional context for the round

        Returns:
            Round result with questions/answers and evaluation
        """
        logger.info(f"Executing placement round '{round_type}' for student {student_id}")

        skill_map = {
            "aptitude": "placement.aptitude.skill.AptitudeSkill",
            "coding": "placement.coding.skill.CodingSkill",
            "technical": "placement.technical.skill.TechnicalSkill",
            "interview": "placement.interview.skill.InterviewSkill",
            "hr": "placement.hr.skill.HRSkill",
        }

        skill_path = skill_map.get(round_type)
        if not skill_path:
            raise ValueError(f"Unknown placement round: {round_type}")

        module_path, class_name = skill_path.rsplit(".", 1)
        import importlib
        module = importlib.import_module(module_path)
        skill_class = getattr(module, class_name)
        skill = skill_class(llm=self.llm, memory=self.memory, student_id=student_id)

        result = await skill.execute(context=context or {})

        # Evaluate the result
        eval_result = self.evaluator.evaluate_round(
            student_id=student_id,
            round_type=round_type,
            result=result.model_dump() if hasattr(result, "model_dump") else result
        )

        logger.info(f"Placement round '{round_type}' completed for student {student_id}, score: {eval_result.get('score', 0)}")
        return {
            "round_type": round_type,
            "result": result.model_dump() if hasattr(result, "model_dump") else result,
            "evaluation": eval_result
        }

    async def submit_answer(self, student_id: str, round_type: str, answer: Any) -> Dict[str, Any]:
        """
        Submit an answer for the current placement round.

        Args:
            student_id: The student's ID
            round_type: Current round type
            answer: Student's answer

        Returns:
            Evaluation result
        """
        logger.info(f"Submitting answer for round '{round_type}' for student {student_id}")

        # For coding round, evaluate code execution
        if round_type == "coding":
            return await self._evaluate_coding_answer(student_id, answer)

        # For other rounds, use the evaluator
        return self.evaluator.evaluate_answer(
            student_id=student_id,
            round_type=round_type,
            answer=answer
        )

    async def _evaluate_coding_answer(self, student_id: str, answer: Any) -> Dict[str, Any]:
        """
        Evaluate coding answer using test cases.
        """
        from placement.coding.evaluator import CodingEvaluator
        evaluator = CodingEvaluator()
        return await evaluator.evaluate(answer)

    def _check_readiness(self, student_id: str) -> Dict[str, Any]:
        """
        Check if student is ready for placement simulation.
        """
        profile = self.memory.get_profile(student_id)
        if not profile:
            return {"ready": False, "reason": "Student profile not found"}

        readiness_score = profile.get("readiness_score", 0)
        if readiness_score < 50:
            return {
                "ready": False,
                "reason": f"Readiness score {readiness_score} is below threshold 50. Complete more learning first."
            }

        return {"ready": True, "reason": "Ready for placement simulation"}

    async def end_simulation(self, student_id: str) -> Dict[str, Any]:
        """
        End the placement simulation and generate the final report.
        """
        logger.info(f"Ending placement simulation for student {student_id}")

        report = await self.report_generator.generate(student_id)

        logger.info(f"Placement simulation ended for student {student_id}")
        return report
