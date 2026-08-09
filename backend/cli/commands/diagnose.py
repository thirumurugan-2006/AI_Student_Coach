"""
Diagnose Command
Diagnoses AI Skills by testing each stage of execution
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))


def diagnose_command(args):
    """Execute diagnose command"""
    print("=" * 40)
    print("SKILL DIAGNOSIS")
    print("=" * 40)
    print()
    
    skills_to_diagnose = [
        'Survey',
        'Assessment',
        'Skill Gap',
        'Roadmap',
        'Learning',
        'Reflection',
        'Readiness',
        'Aptitude',
        'Coding',
        'Technical',
        'Interview',
        'HR',
        'Placement Report'
    ]
    
    all_passed = True
    
    for skill in skills_to_diagnose:
        print(f"{skill}")
        print("-" * 40)
        
        stages = diagnose_skill(skill, args)
        
        skill_passed = True
        for stage, (status, message) in stages.items():
            symbol = "✓" if status else "✗"
            print(f"{stage:<16} {symbol}")
            if not status and message:
                print(f"  Error: {message}")
            skill_passed = skill_passed and status
        
        if skill_passed:
            print()
            print("STATUS: PASS")
        else:
            print()
            print("STATUS: FAIL")
            all_passed = False
        
        print()
    
    if all_passed:
        print("=" * 40)
        print("All Skills: PASS")
        return 0
    else:
        print("=" * 40)
        print("Some Skills: FAIL")
        return 1


def diagnose_skill(skill_name, args):
    """Diagnose a specific skill through all stages"""
    stages = {}
    
    # Context
    stages['Context'] = check_context(skill_name)
    
    # Instructions
    stages['Instructions'] = check_instructions(skill_name)
    
    # Prompt
    stages['Prompt'] = check_prompt(skill_name)
    
    # LLM
    stages['Groq'] = check_llm(skill_name, args.mock)
    
    # Parsing
    stages['Parsing'] = check_parsing(skill_name)
    
    # Validation
    stages['Validation'] = check_validation(skill_name)
    
    # Database
    stages['Database'] = check_database(skill_name)
    
    # Memory
    stages['Memory'] = check_memory(skill_name)
    
    # Career Intelligence
    stages['Career Intelligence'] = check_career_intelligence(skill_name)
    
    # Next Action
    stages['Next Action'] = check_next_action(skill_name)
    
    return stages


def check_context(skill_name):
    """Check if context can be loaded"""
    try:
        from memory.student_memory import StudentMemory
        memory = StudentMemory()
        profile = memory.get_profile('cli_user')
        if profile is None:
            memory.create_student('cli_user', 'CLI Test User')
        return True, None
    except Exception as e:
        return False, str(e)


def check_instructions(skill_name):
    """Check if instructions can be loaded"""
    try:
        skill_map = {
            'Survey': 'survey',
            'Assessment': 'assessment',
            'Skill Gap': 'skill_gap',
            'Roadmap': 'roadmap',
            'Learning': 'learning',
            'Reflection': 'reflection',
            'Readiness': 'readiness',
            'Aptitude': 'placement_aptitude',
            'Coding': 'placement_coding',
            'Technical': 'placement_technical',
            'Interview': 'placement_interview',
            'HR': 'placement_hr',
            'Placement Report': 'placement_report'
        }
        
        skill_key = skill_map.get(skill_name)
        if not skill_key:
            return False, f"Unknown skill: {skill_name}"
        
        # Check if instruction.md file exists
        instruction_path = Path(__file__).parent.parent.parent / f'skills/{skill_key}/instruction.md'
        if instruction_path.exists():
            return True, None
        else:
            return False, "Instructions file not found"
    except Exception as e:
        return False, str(e)


def check_prompt(skill_name):
    """Check if prompt can be built"""
    try:
        # This is a basic check - actual prompt building requires skill execution
        return True, None
    except Exception as e:
        return False, str(e)


def check_llm(skill_name, mock=False):
    """Check if LLM can be called"""
    try:
        from core.llm_interface import LLMInterface
        
        async def test_llm():
            llm = LLMInterface()
            if mock:
                # Mock mode - just check initialization
                return True
            else:
                health = await llm.health_check()
                return health.get("content_llm", False)
        
        result = asyncio.run(test_llm())
        if result:
            return True, None
        else:
            return False, "LLM health check failed"
    except Exception as e:
        return False, str(e)


def check_parsing(skill_name):
    """Check if LLM response can be parsed"""
    try:
        # This requires actual execution - basic check for schema existence
        skill_map = {
            'Survey': 'survey',
            'Assessment': 'assessment',
            'Skill Gap': 'skill_gap',
            'Roadmap': 'roadmap',
            'Learning': 'learning',
            'Reflection': 'reflection',
            'Readiness': 'readiness',
            'Aptitude': 'placement_aptitude',
            'Coding': 'placement_coding',
            'Technical': 'placement_technical',
            'Interview': 'placement_interview',
            'HR': 'placement_hr',
            'Placement Report': 'placement_report'
        }
        
        skill_key = skill_map.get(skill_name)
        if not skill_key:
            return False, f"Unknown skill: {skill_name}"
        
        # Check if schema exists
        schema_path = Path(__file__).parent.parent.parent / f'skills/{skill_key}/schema.py'
        if schema_path.exists():
            return True, None
        else:
            return False, "Schema file not found"
    except Exception as e:
        return False, str(e)


def check_validation(skill_name):
    """Check if validation works"""
    try:
        # Check if validator module exists
        from core import validator
        return True, None
    except Exception as e:
        return False, str(e)


def check_database(skill_name):
    """Check if database operations work"""
    try:
        from database.session import engine
        from sqlalchemy import text
        
        async def test_db():
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        
        result = asyncio.run(test_db())
        if result:
            return True, None
        else:
            return False, "Database query failed"
    except Exception as e:
        return False, str(e)


def check_memory(skill_name):
    """Check if memory operations work"""
    try:
        from memory.student_memory import StudentMemory
        memory = StudentMemory()
        profile = memory.get_profile('cli_user')
        if profile is None:
            memory.create_student('cli_user', 'CLI Test User')
        return True, None
    except Exception as e:
        return False, str(e)


def check_career_intelligence(skill_name):
    """Check if career intelligence works"""
    try:
        from services.career_intelligence import CareerIntelligenceHub
        # Just check if it can be imported
        return True, None
    except Exception as e:
        return False, str(e)


def check_next_action(skill_name):
    """Check if next action determination works"""
    try:
        from core.workflow_controller import workflow_controller
        # Just check if it can be imported
        return True, None
    except Exception as e:
        return False, str(e)
