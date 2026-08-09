"""
Survey Answer Command
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from cli.utils import run_pipeline_command


def survey_answer_command(args):
    """Submit an answer to a survey question."""
    if not args.question_id or not args.answer:
        print("✗ --question-id and --answer are required for survey-answer")
        return 1

    return run_pipeline_command(
        args,
        skill_name="survey_answer",
        title="Survey Answer",
        additional_context={
            "question_id": args.question_id,
            "user_answer": args.answer,
        },
    )
