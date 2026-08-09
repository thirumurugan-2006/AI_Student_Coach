"""
Skill Gap Command
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from cli.utils import run_pipeline_command


def skill_gap_command(args):
    """Execute skill-gap analysis."""
    return run_pipeline_command(args, skill_name="skill_gap", title="Skill Gap Analysis")
