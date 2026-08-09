"""
Benchmark Command
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from cli.utils import benchmark_pipelines


def benchmark_command(args):
    """Run pipeline performance benchmarks."""
    return benchmark_pipelines(args.mock, args.user_id)
