"""
Survey Command
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))


def survey_command(args):
    """Execute survey command"""
    print("=" * 40)
    print("SURVEY")
    print("=" * 40)
    print()
    
    if args.mock:
        return run_mock_survey(args)
    else:
        return run_real_survey(args)


def run_mock_survey(args):
    """Run survey with mock LLM"""
    print("Mode: MOCK (using MockLLM)")
    print()
    
    try:
        from core.mock_llm import MockLLM
        from memory.student_memory import StudentMemory
        from pipelines.preparation.survey_pipeline import SurveyPipeline
        from pipelines.pipeline_context import PipelineContext
        
        # Initialize components
        mock_llm = MockLLM()
        memory = StudentMemory()
        
        # Create student if not exists
        user_id = args.user_id
        profile = memory.get_profile(user_id)
        if not profile:
            memory.create_student(user_id, "CLI Test User")
            print(f"Created student: {user_id}")
        
        # Create pipeline with mock LLM
        pipeline = SurveyPipeline(llm=mock_llm, memory=memory)
        
        # Build context
        context = PipelineContext(
            student_id=user_id,
            current_module="preparation",
            current_skill="survey",
            workflow_state="survey_in_progress",
            student_memory=profile or {},
            career_intelligence={},
            target_role=None,
            skill_gaps=[],
            question_history=[],
            previous_result=None,
            additional_context={"user_message": "Start survey"}
        )
        
        print("Executing SurveyPipeline with MockLLM...")
        print()
        
        # Execute pipeline
        result = asyncio.run(pipeline.execute(context))
        
        # Display result
        if result.status == "success":
            print("✓ Survey execution successful")
            print()
            
            # Extract question from result
            if hasattr(result, 'result') and result.result:
                survey_data = result.result
                if 'mcq_question' in survey_data:
                    question = survey_data['mcq_question']
                    print("Question:")
                    print(question.get('question', 'No question'))
                    print()
                    print("Options:")
                    for i, option in enumerate(question.get('options', []), 1):
                        print(f"  {i}. {option}")
                else:
                    print("No question in result")
            else:
                print("No result data")
            
            print()
            print(f"Next Action: {result.next_action}")
            print(f"Progress: {result.progress * 100:.0f}%")
            
            return 0
        else:
            print(f"✗ Survey execution failed: {result.error_message}")
            return 1
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def run_real_survey(args):
    """Run survey with real Groq LLM"""
    print("Mode: REAL (using Groq)")
    print()
    
    try:
        from core.llm_interface import LLMInterface
        from memory.student_memory import StudentMemory
        from pipelines.preparation.survey_pipeline import SurveyPipeline
        from pipelines.pipeline_context import PipelineContext
        
        # Initialize components
        llm = LLMInterface()
        memory = StudentMemory()
        
        # Create student if not exists
        user_id = args.user_id
        profile = memory.get_profile(user_id)
        if not profile:
            memory.create_student(user_id, "CLI Test User")
            print(f"Created student: {user_id}")
        
        # Create pipeline with real LLM
        pipeline = SurveyPipeline(llm=llm, memory=memory)
        
        # Build context
        context = PipelineContext(
            student_id=user_id,
            current_module="preparation",
            current_skill="survey",
            workflow_state="survey_in_progress",
            student_memory=profile or {},
            career_intelligence={},
            target_role=None,
            skill_gaps=[],
            question_history=[],
            previous_result=None,
            additional_context={"user_message": "Start survey"}
        )
        
        print("Executing SurveyPipeline with Groq...")
        print()
        
        # Execute pipeline
        result = asyncio.run(pipeline.execute(context))
        
        # Display result
        if result.status == "success":
            print("✓ Survey execution successful")
            print()
            
            # Extract question from result
            if hasattr(result, 'result') and result.result:
                survey_data = result.result
                if 'mcq_question' in survey_data:
                    question = survey_data['mcq_question']
                    print("Question:")
                    print(question.get('question', 'No question'))
                    print()
                    print("Options:")
                    for i, option in enumerate(question.get('options', []), 1):
                        print(f"  {i}. {option}")
                else:
                    print("No question in result")
            else:
                print("No result data")
            
            print()
            print(f"Next Action: {result.next_action}")
            print(f"Progress: {result.progress * 100:.0f}%")
            
            return 0
        else:
            print(f"✗ Survey execution failed: {result.error_message}")
            return 1
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
