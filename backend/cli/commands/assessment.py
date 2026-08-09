"""
Assessment Command
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from cli.utils import run_pipeline_command


def assessment_command(args):
    """Execute assessment command."""
    topic = args.topic or "Python"
    additional = {"topic": topic}
    if args.question_id and args.answer:
        return run_pipeline_command(
            args,
            skill_name="assessment_answer",
            title="Assessment Answer",
            additional_context={
                "question_id": args.question_id,
                "user_answer": args.answer,
                "topic": topic,
            },
        )
    return run_pipeline_command(
        args,
        skill_name="assessment",
        title="Assessment",
        additional_context=additional,
    )
