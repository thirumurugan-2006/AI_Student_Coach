"""
Main CLI Entry Point for AI Career Coach
"""
import sys
import argparse
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from cli.commands.health import health_command
from cli.commands.diagnose import diagnose_command
from cli.commands.survey import survey_command
from cli.commands.survey_answer import survey_answer_command
from cli.commands.assessment import assessment_command
from cli.commands.skill_gap import skill_gap_command
from cli.commands.roadmap import roadmap_command
from cli.commands.learning import learning_command
from cli.commands.reflection import reflection_command
from cli.commands.readiness import readiness_command
from cli.commands.placement import placement_command
from cli.commands.run import run_command
from cli.commands.benchmark import benchmark_command
from cli.commands.test import test_command


def main():
    parser = argparse.ArgumentParser(
        description="AI Career Coach CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  health          Check system health
  diagnose        Diagnose AI skills
  survey          Run survey
  survey-answer   Submit a survey answer
  assessment      Run assessment
  skill-gap       Run skill gap analysis
  roadmap         Generate roadmap
  learning        Run learning module
  reflection      Run reflection
  readiness       Check readiness
  placement       Run placement simulation
  run             Full workflow
  benchmark       Performance benchmark
  test            Run automated tests
        """
    )

    parser.add_argument(
        'command',
        choices=[
            'health', 'diagnose', 'survey', 'survey-answer', 'assessment',
            'skill-gap', 'roadmap', 'learning', 'reflection', 'readiness',
            'placement', 'run', 'benchmark', 'test',
        ],
        help='Command to execute'
    )

    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--mock', action='store_true', help='Use mock LLM')
    parser.add_argument('--user-id', type=str, default='cli_user', help='User ID')
    parser.add_argument('--question-id', type=str, default=None, help='Question ID for answer commands')
    parser.add_argument('--answer', type=str, default=None, help='Answer text for answer commands')
    parser.add_argument('--topic', type=str, default=None, help='Topic for assessment/roadmap/learning')
    parser.add_argument('--message', type=str, default=None, help='Message for reflection')
    parser.add_argument(
        '--round',
        type=str,
        default='aptitude',
        choices=['aptitude', 'coding', 'technical', 'interview', 'hr', 'report'],
        help='Placement round to run',
    )

    args = parser.parse_args()

    command_map = {
        'health': health_command,
        'diagnose': diagnose_command,
        'survey': survey_command,
        'survey-answer': survey_answer_command,
        'assessment': assessment_command,
        'skill-gap': skill_gap_command,
        'roadmap': roadmap_command,
        'learning': learning_command,
        'reflection': reflection_command,
        'readiness': readiness_command,
        'placement': placement_command,
        'run': run_command,
        'benchmark': benchmark_command,
        'test': test_command,
    }

    command_func = command_map.get(args.command)
    if command_func:
        return command_func(args)
    print(f"Unknown command: {args.command}")
    return 1


if __name__ == '__main__':
    sys.exit(main())
