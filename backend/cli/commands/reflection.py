"""
Reflection Command
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from cli.utils import run_pipeline_command


def reflection_command(args):
    """Run reflection module."""
    message = args.message or "I learned a lot about my career goals today."
    return run_pipeline_command(
        args,
        skill_name="reflection",
        title="Reflection",
        additional_context={"reflection_note": message},
    )
