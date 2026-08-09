"""
Placement Command
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from cli.utils import run_pipeline_command, PLACEMENT_ROUNDS


def placement_command(args):
    """Execute placement simulation round."""
    round_name = (args.round or "aptitude").lower()
    if round_name not in PLACEMENT_ROUNDS:
        print(f"✗ Unknown round: {round_name}")
        print(f"  Available: {', '.join(PLACEMENT_ROUNDS.keys())}")
        return 1

    skill_name = PLACEMENT_ROUNDS[round_name]
    return run_pipeline_command(
        args,
        skill_name=skill_name,
        title=f"Placement {round_name.title()} Round",
    )
