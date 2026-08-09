"""
Test Command - Automated Tests and Integration Verification
"""
import sys
import subprocess
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from cli.utils import run_verification_suite, PREPARATION_SKILLS, execute_pipeline, get_pipeline_class
import asyncio


def test_command(args):
    """Run automated tests and integration verification."""
    print("=" * 40)
    print("AUTOMATED TESTS")
    print("=" * 40)
    print()

    # Step 7 & 8: Verify integrations
    verify_result = run_verification_suite()
    print()

    # Import checks for all pipelines
    print("Pipeline Import Checks:")
    import_ok = True
    for skill in PREPARATION_SKILLS + list({
        "placement_aptitude", "placement_coding", "placement_technical",
        "placement_interview", "placement_hr", "placement_report"
    }):
        try:
            get_pipeline_class(skill)
            print(f"  {skill:<22} OK")
        except Exception as e:
            print(f"  {skill:<22} FAIL ({e})")
            import_ok = False

    print()

    # Mock pipeline smoke tests
    if args.mock:
        print("Mock Pipeline Smoke Tests:")
        smoke_ok = True
        context_map = {
            "survey": {"user_message": "Start survey"},
            "assessment": {"topic": "Python"},
            "skill_gap": {},
            "roadmap": {"topic_request": "Python"},
            "learning": {"topic": "Python"},
            "reflection": {"reflection_note": "Test reflection"},
            "readiness": {},
        }
        for skill in PREPARATION_SKILLS:
            try:
                result = asyncio.run(
                    execute_pipeline(skill, args.user_id, True, context_map.get(skill, {}))
                )
                status = "OK" if result.status == "success" else "FAIL"
                print(f"  {skill:<22} {status}")
                if result.status != "success":
                    smoke_ok = False
            except Exception as e:
                print(f"  {skill:<22} FAIL ({e})")
                smoke_ok = False
        print()
    else:
        smoke_ok = True
        print("Skipping smoke tests (use --mock to run pipeline smoke tests)")
        print()

    # Run pytest if available
    pytest_ok = True
    tests_dir = backend_dir / "tests"
    if tests_dir.exists():
        print("Running pytest suite...")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(tests_dir), "-q", "--tb=no"],
            cwd=str(backend_dir),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("  pytest: PASS")
        else:
            print("  pytest: FAIL")
            if args.debug and result.stdout:
                print(result.stdout)
            pytest_ok = False
        print()

    all_ok = verify_result == 0 and import_ok and smoke_ok and pytest_ok
    print("=" * 40)
    print("ALL TESTS PASS" if all_ok else "SOME TESTS FAILED")
    return 0 if all_ok else 1
