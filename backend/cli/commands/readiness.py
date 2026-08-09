"""
Readiness Command
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from cli.utils import run_pipeline_command


def readiness_command(args):
    """Check placement readiness."""
    return run_pipeline_command(args, skill_name="readiness", title="Readiness Gate")
