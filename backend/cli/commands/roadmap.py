"""
Roadmap Command
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from cli.utils import run_pipeline_command


def roadmap_command(args):
    """Generate learning roadmap."""
    topic = args.topic or "Full-stack web development"
    return run_pipeline_command(
        args,
        skill_name="roadmap",
        title="Learning Roadmap",
        additional_context={"topic_request": topic},
    )
