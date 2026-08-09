"""
Shared utilities for CLI commands.
"""
import asyncio
import json
import time
from typing import Any, Dict, Optional, Type

from memory.student_memory import StudentMemory
from services.career_intelligence import CareerIntelligenceHub
from pipelines.pipeline_context import PipelineContext
from pipelines.pipeline_result import PipelineResult


PIPELINE_REGISTRY = {
    "survey": ("pipelines.preparation.survey_pipeline", "SurveyPipeline"),
    "survey_answer": ("pipelines.preparation.survey_answer_pipeline", "SurveyAnswerPipeline"),
    "assessment": ("pipelines.preparation.assessment_pipeline", "AssessmentPipeline"),
    "assessment_answer": ("pipelines.preparation.assessment_answer_pipeline", "AssessmentAnswerPipeline"),
    "skill_gap": ("pipelines.preparation.skill_gap_pipeline", "SkillGapPipeline"),
    "roadmap": ("pipelines.preparation.roadmap_pipeline", "RoadmapPipeline"),
    "learning": ("pipelines.preparation.learning_pipeline", "LearningPipeline"),
    "reflection": ("pipelines.preparation.reflection_pipeline", "ReflectionPipeline"),
    "readiness": ("pipelines.preparation.readiness_pipeline", "ReadinessPipeline"),
    "placement_aptitude": ("pipelines.placement.aptitude_pipeline", "AptitudePipeline"),
    "placement_coding": ("pipelines.placement.coding_pipeline", "CodingPipeline"),
    "placement_technical": ("pipelines.placement.technical_pipeline", "TechnicalPipeline"),
    "placement_interview": ("pipelines.placement.interview_pipeline", "InterviewPipeline"),
    "placement_hr": ("pipelines.placement.hr_pipeline", "HRPipeline"),
    "placement_report": ("pipelines.placement.placement_report_pipeline", "PlacementReportPipeline"),
}

PREPARATION_SKILLS = [
    "survey", "assessment", "skill_gap", "roadmap", "learning", "reflection", "readiness"
]

PLACEMENT_ROUNDS = {
    "aptitude": "placement_aptitude",
    "coding": "placement_coding",
    "technical": "placement_technical",
    "interview": "placement_interview",
    "hr": "placement_hr",
    "report": "placement_report",
}


def get_llm(use_mock: bool):
    if use_mock:
        from core.mock_llm import MockLLM
        return MockLLM()
    from core.llm_interface import LLMInterface
    return LLMInterface()


def ensure_student(memory: StudentMemory, user_id: str, name: str = "CLI Test User") -> dict:
    profile = memory.get_profile(user_id)
    if not profile:
        memory.create_student(user_id, name)
        print(f"Created student: {user_id}")
        profile = memory.get_profile(user_id)
    return profile


def get_pipeline_class(skill_name: str) -> Type:
    if skill_name not in PIPELINE_REGISTRY:
        raise ValueError(f"Unknown pipeline: {skill_name}")
    module_path, class_name = PIPELINE_REGISTRY[skill_name]
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def build_context(
    user_id: str,
    skill_name: str,
    profile: dict,
    career_intel: CareerIntelligenceHub,
    additional_context: Optional[Dict[str, Any]] = None,
) -> PipelineContext:
    module = "placement" if skill_name.startswith("placement_") else "preparation"
    return PipelineContext(
        student_id=user_id,
        current_module=module,
        current_skill=skill_name,
        workflow_state=f"{skill_name}_in_progress",
        student_memory=profile or {},
        career_intelligence=career_intel.get_student_intelligence(user_id),
        target_role=profile.get("career_goal") if profile else None,
        skill_gaps=profile.get("weak_topics", []) if profile else [],
        question_history=[],
        previous_result=None,
        additional_context=additional_context or {},
    )


async def execute_pipeline(
    skill_name: str,
    user_id: str,
    use_mock: bool,
    additional_context: Optional[Dict[str, Any]] = None,
) -> PipelineResult:
    llm = get_llm(use_mock)
    memory = StudentMemory()
    career_intel = CareerIntelligenceHub()
    profile = ensure_student(memory, user_id)

    pipeline_class = get_pipeline_class(skill_name)
    pipeline = pipeline_class(llm=llm, memory=memory, career_intelligence=career_intel)
    context = build_context(user_id, skill_name, profile, career_intel, additional_context)
    return await pipeline.execute(context)


def run_pipeline_command(
    args,
    skill_name: str,
    title: str,
    additional_context: Optional[Dict[str, Any]] = None,
) -> int:
    print("=" * 40)
    print(title.upper())
    print("=" * 40)
    print()
    print(f"Mode: {'MOCK' if args.mock else 'REAL'}")
    print(f"User: {args.user_id}")
    print()

    try:
        result = asyncio.run(
            execute_pipeline(skill_name, args.user_id, args.mock, additional_context)
        )
        return print_pipeline_result(result)
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


def print_pipeline_result(result: PipelineResult) -> int:
    if result.status == "success":
        print("[OK] Execution successful")
        print()
        if result.result:
            print("Result:")
            print(json.dumps(result.result, indent=2, default=str))
        print()
        print(f"Next Action: {result.next_action}")
        print(f"Reason: {result.next_action_reason}")
        print(f"Progress: {result.progress * 100:.0f}%")
        return 0

    print(f"[FAIL] Execution failed: {result.error_message}")
    return 1


async def verify_memory_integration(user_id: str = "verify_memory_user") -> bool:
    memory = StudentMemory()
    memory.create_student(user_id, "Verify User")
    memory.update_goal(user_id, "Software Engineer")
    memory.update_skill(user_id, "Python", 75)

    profile = memory.get_profile(user_id)
    return (
        profile is not None
        and profile.get("career_goal") == "Software Engineer"
        and profile.get("skills", {}).get("Python") == 75
    )


async def verify_career_intelligence_integration(user_id: str = "verify_ci_user") -> bool:
    hub = CareerIntelligenceHub()
    hub.update_profile(user_id, career_goal="Data Scientist", target_role="ML Engineer")
    hub.add_evidence(user_id, "assessment", "Python", 0.85, is_correct=True)
    hub.update_skill_gaps(user_id, ["System Design"], source="assessment")

    intel = hub.get_student_intelligence(user_id)
    return (
        len(intel.get("evidence", [])) >= 1
        and "System Design" in intel.get("skill_gaps", [])
    )


def run_verification_suite() -> int:
    print("=" * 40)
    print("INTEGRATION VERIFICATION")
    print("=" * 40)
    print()

    memory_ok = asyncio.run(verify_memory_integration())
    print(f"Database + Memory: {'PASS' if memory_ok else 'FAIL'}")

    ci_ok = asyncio.run(verify_career_intelligence_integration())
    print(f"Career Intelligence: {'PASS' if ci_ok else 'FAIL'}")

    print()
    return 0 if memory_ok and ci_ok else 1


def benchmark_pipelines(use_mock: bool, user_id: str) -> int:
    print("=" * 40)
    print("PIPELINE BENCHMARK")
    print("=" * 40)
    print()

    skills = PREPARATION_SKILLS[:3]  # benchmark key pipelines
    for skill in skills:
        context_map = {
            "survey": {"user_message": "Start survey"},
            "assessment": {"topic": "Python"},
            "skill_gap": {},
        }
        start = time.perf_counter()
        try:
            asyncio.run(execute_pipeline(skill, user_id, use_mock, context_map.get(skill, {})))
            elapsed = time.perf_counter() - start
            print(f"{skill:<20} {elapsed:.3f}s  OK")
        except Exception as e:
            elapsed = time.perf_counter() - start
            print(f"{skill:<20} {elapsed:.3f}s  FAIL ({e})")

    print()
    return 0
