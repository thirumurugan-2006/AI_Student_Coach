"""
Run Command - Full Workflow
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from cli.utils import (
    PREPARATION_SKILLS,
    PLACEMENT_ROUNDS,
    execute_pipeline,
    print_pipeline_result,
    ensure_student,
)
import asyncio
from memory.student_memory import StudentMemory


WORKFLOW_STEPS = [
    ("survey", {"user_message": "Start survey"}),
    ("assessment", {"topic": "Python"}),
    ("skill_gap", {}),
    ("roadmap", {"topic_request": "Full-stack development"}),
    ("learning", {"topic": "Python"}),
    ("reflection", {"reflection_note": "Completed learning module"}),
    ("readiness", {}),
]


def run_command(args):
    """Execute full preparation + placement workflow."""
    print("=" * 40)
    print("FULL WORKFLOW")
    print("=" * 40)
    print()
    print(f"Mode: {'MOCK' if args.mock else 'REAL'}")
    print(f"User: {args.user_id}")
    print()

    memory = StudentMemory()
    ensure_student(memory, args.user_id)

    all_ok = True

    for skill_name, context in WORKFLOW_STEPS:
        print(f"--- {skill_name} ---")
        try:
            result = asyncio.run(
                execute_pipeline(skill_name, args.user_id, args.mock, context)
            )
            if result.status != "success":
                print(f"✗ {skill_name} failed: {result.error_message}")
                all_ok = False
                if not args.debug:
                    break
            else:
                print(f"✓ {skill_name} → next: {result.next_action}")
        except Exception as e:
            print(f"✗ {skill_name} error: {e}")
            all_ok = False
            if not args.debug:
                break
        print()

    if all_ok:
        print("--- Placement Rounds ---")
        for round_name, skill_name in PLACEMENT_ROUNDS.items():
            print(f"--- {skill_name} ---")
            try:
                result = asyncio.run(
                    execute_pipeline(skill_name, args.user_id, args.mock, {})
                )
                if result.status != "success":
                    print(f"✗ {skill_name} failed: {result.error_message}")
                    all_ok = False
                else:
                    print(f"✓ {skill_name} → next: {result.next_action}")
            except Exception as e:
                print(f"✗ {skill_name} error: {e}")
                all_ok = False
            print()

    print("=" * 40)
    print("WORKFLOW COMPLETE" if all_ok else "WORKFLOW FAILED")
    return 0 if all_ok else 1
