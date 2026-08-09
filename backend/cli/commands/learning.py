"""
Learning Command
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from cli.utils import run_pipeline_command


def learning_command(args):
    """Run learning module."""
    topic = args.topic or "Python fundamentals"
    return run_pipeline_command(
        args,
        skill_name="learning",
        title="Learning Module",
        additional_context={"topic": topic},
    )
