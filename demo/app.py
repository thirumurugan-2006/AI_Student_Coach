"""
AI Career Coach - Streamlit Demo Frontend

A demonstration frontend for the AI Career Coach system.
Follows the architecture: Streamlit → FastAPI → Planner → Career Coach → Router → Skills → Evaluation → Memory → Database → Recommendation → Streamlit
"""

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PAGE_CONFIG, UI_CONFIG
from state import init_session_state, reset_session_state
from components import render_sidebar, render_progress, render_info_card, render_stat_card, render_question_input, render_recommendations, render_readiness_chart, render_progress_chart
from utils import handle_api_error, show_loading, show_success, format_readiness_score, format_stage_name
from api import client, user_service, survey_service, assessment_service, skill_gap_service, roadmap_service, learning_service, interview_service, reflection_service, readiness_service, dashboard_service, placement_service, career_intelligence_service, coach_service, workflow_service
from navigation import handle_workflow_transition, resolve_navigation, get_current_stage_info


def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(**PAGE_CONFIG)
    
    # Initialize session state
    init_session_state()
    
    # Check backend health
    if not st.session_state["backend_healthy"]:
        try:
            st.session_state["backend_healthy"] = client.check_health()
        except Exception as e:
            st.session_state["backend_healthy"] = False
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    if not st.session_state["backend_healthy"]:
        render_backend_error()
    elif not st.session_state["user"]:
        render_onboarding()
    else:
        render_workflow()


def render_backend_error():
    """Render backend error screen."""
    st.error("❌ Backend is not running")
    st.markdown("""
    ### Backend Connection Failed
    
    The AI Career Coach backend is not available. Please ensure:
    
    1. The backend is running on http://localhost:8001
    2. Groq API key is configured in backend/.env
    3. Groq API is accessible
    
    **To start the backend:**
    ```bash
    cd backend
    uvicorn main:app --reload --port 8001
    ```
    
    **To configure Groq:**
    ```bash
    # Edit backend/.env
    GROQ_API_KEY=your-groq-api-key-here
    ```
    
    **Get a Groq API key:**
    Visit https://console.groq.com/keys
    """)
    
    if st.button("🔄 Retry Connection", key="retry_connection"):
        st.rerun()


def render_onboarding():
    """Render user onboarding screen."""
    st.markdown("# 🎯 Welcome to AI Career Coach")
    st.markdown("### Your Personal AI-Powered Career Development Assistant")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### What We Offer:
        - 📊 **Career Discovery**: Identify your ideal career path
        - 📚 **Skill Assessment**: Evaluate your current skill level
        - 🎓 **Personalized Learning**: Custom learning roadmaps
        - 💼 **Mock Interviews**: Practice with AI recruiters
        - 🤔 **Reflection**: Track your growth and insights
        """)
    
    with col2:
        st.markdown("""
        ### How It Works:
        1. Create your profile
        2. Complete career survey
        3. Take skill assessments
        4. Follow your learning roadmap
        5. Practice with mock interviews
        6. Reflect on your progress
        7. Track your overall growth
        """)
    
    st.markdown("---")
    
    st.markdown("### 🚀 Get Started")
    
    with st.form("signup_form"):
        name = st.text_input("Your Name", placeholder="Enter your full name")
        email = st.text_input("Email Address", placeholder="Enter your email")
        
        submit_button = st.form_submit_button("Start Career Journey", type="primary")
        
        if submit_button:
            if not name or not email:
                st.error("Please fill in all fields")
                return
            
            try:
                with show_loading("Creating your profile..."):
                    response = user_service.signup(name, email)
                
                # Store user session
                st.session_state["user"] = {
                    "user_id": response["user_id"],
                    "name": response["name"],
                    "email": response["email"]
                }
                st.session_state["user_id"] = response["user_id"]
                st.session_state["access_token"] = response["access_token"]
                st.session_state["current_stage"] = "survey"
                
                show_success(response["message"])
                st.rerun()
                
            except Exception as e:
                handle_api_error(e, "Signup")


def render_workflow():
    """Render main workflow based on current stage from backend."""
    current_stage = st.session_state["current_stage"]
    
    # Fetch workflow state from backend
    if st.session_state.get("user_id") and st.session_state.get("access_token"):
        try:
            user_id = st.session_state["user_id"]
            access_token = st.session_state.get("access_token")
            workflow_state = workflow_service.get_workflow_state(user_id, access_token)
            
            # Cache backend workflow state
            st.session_state["backend_workflow_state"] = workflow_state
            
            # Update progress from backend
            backend_progress = workflow_state.get("progress", 0)
            st.session_state["workflow_progress"] = backend_progress
            
            # Check if backend has provided a next_action to override current stage
            next_action = workflow_state.get("next_action")
            if next_action and next_action != current_stage:
                target_stage = resolve_navigation(next_action)
                st.session_state["current_stage"] = target_stage
                st.session_state["next_action"] = None  # Clear after processing
                st.rerun()
                return
        except Exception as e:
            # If backend call fails, continue with current state
            pass
    
    # Check if session state has a pending next_action
    if "next_action" in st.session_state and st.session_state["next_action"]:
        next_action = st.session_state["next_action"]
        target_stage = resolve_navigation(next_action)
        
        # Only update if different to avoid unnecessary reruns
        if target_stage != current_stage:
            st.session_state["current_stage"] = target_stage
            st.session_state["next_action"] = None  # Clear after processing
            st.rerun()
            return
    
    # Render progress indicator
    render_progress(current_stage)
    
    # Display current stage info header
    stage_info = get_current_stage_info()
    st.markdown(f"### {stage_info.get('icon', '📊')} {stage_info.get('name', 'Dashboard')}")
    st.markdown(f"**Module:** {stage_info.get('module', 'Career Intelligence')}")
    
    st.markdown("---")
    
    # Route to appropriate stage using centralized navigation
    if current_stage == "survey":
        render_survey_stage()
    elif current_stage == "assessment":
        render_assessment_stage()
    elif current_stage == "skill_gap":
        render_skill_gap_stage()
    elif current_stage == "roadmap":
        render_roadmap_stage()
    elif current_stage == "learning":
        render_learning_stage()
    elif current_stage == "reflection":
        render_reflection_stage()
    elif current_stage == "readiness":
        render_readiness_stage()
    elif current_stage == "placement_aptitude":
        render_placement_aptitude_stage()
    elif current_stage == "placement_coding":
        render_placement_coding_stage()
    elif current_stage == "placement_technical":
        render_placement_technical_stage()
    elif current_stage == "placement_interview":
        render_placement_interview_stage()
    elif current_stage == "placement_hr":
        render_placement_hr_stage()
    elif current_stage == "placement_report":
        render_placement_report_stage()
    elif current_stage == "dashboard":
        render_dashboard_stage()
    elif current_stage == "career_intelligence":
        render_career_intelligence_stage()
    else:
        st.error(f"Unknown stage: {current_stage}")
        st.session_state["current_stage"] = "dashboard"
        st.rerun()


def render_survey_stage():
    """Render survey stage with MCQ format."""
    st.markdown("## 🎯 Career Discovery Survey")
    
    st.markdown("""
    Let's discover your career goals and preferences through a quick survey.
    Answer the questions to help us personalize your learning journey.
    """)
    
    # Initialize survey state
    if "survey_history" not in st.session_state:
        st.session_state["survey_history"] = []
    if "current_mcq" not in st.session_state:
        st.session_state["current_mcq"] = None
    
    # Show progress
    if len(st.session_state["survey_history"]) > 0:
        st.markdown("### Previous Responses:")
        for i, (question, answer) in enumerate(st.session_state["survey_history"]):
            with st.expander(f"Q{i+1}: {question}"):
                st.markdown(f"**Your Answer:** {answer}")
    
    st.markdown("---")
    
    # Fetch MCQ question from backend if not available
    if st.session_state["current_mcq"] is None:
        try:
            with show_loading("Loading next question..."):
                user_id = st.session_state["user_id"]
                access_token = st.session_state.get("access_token")
                response = survey_service.conduct_survey(user_id, "", access_token)
                
                # Parse MCQ from response
                if "mcq_question" in response and response["mcq_question"]:
                    st.session_state["current_mcq"] = response["mcq_question"]
                else:
                    # Survey completed - get next action from backend
                    workflow_state = workflow_service.get_workflow_state(user_id, access_token)
                    next_action = workflow_state.get("next_action", "assessment")
                    st.session_state["next_action"] = next_action
                    st.rerun()
        except Exception as e:
            handle_api_error(e, "Survey")
            return
    
    # Display MCQ question
    mcq = st.session_state["current_mcq"]
    if mcq:
        st.markdown(f"### {mcq['question']}")
        
        # Display options as radio buttons
        selected_option = st.radio(
            "Select your answer:",
            mcq["options"],
            key=f"mcq_{len(st.session_state['survey_history'])}"
        )
        
        if st.button("Submit Answer", type="primary", key="survey_submit"):
            try:
                with show_loading("Processing your response..."):
                    user_id = st.session_state["user_id"]
                    access_token = st.session_state.get("access_token")
                    question_id = mcq.get("question_id")
                    
                    # Send selected option with question_id
                    answer_data = {
                        "user_message": str(selected_option),
                        "question_id": question_id
                    }
                    response = survey_service.conduct_survey_with_answer(user_id, answer_data, access_token)
                
                # Store in history
                st.session_state["survey_history"].append((mcq["question"], selected_option))
                
                # Clear current MCQ to fetch next
                st.session_state["current_mcq"] = None
                
                show_success(response["response_message"])
                st.rerun()
                    
            except Exception as e:
                handle_api_error(e, "Survey")


def render_assessment_stage():
    """Render assessment stage."""
    st.markdown("## 📝 Skill Assessment")
    
    st.markdown("""
    Let's assess your current skill level in your target area. This helps us identify knowledge gaps and create a personalized learning plan.
    """)
    
    # Topic selection
    topic = st.text_input("What topic would you like to be assessed on?", placeholder="e.g., Python, Machine Learning, System Design")
    
    if not topic:
        st.info("Enter a topic to begin the assessment.")
        return
    
    st.markdown("---")
    
    # Assessment interaction
    if "assessment_question" not in st.session_state:
        st.session_state["assessment_question"] = None
    
    if st.session_state["assessment_question"] is None:
        # Start new assessment
        if st.button("Start Assessment", type="primary", key="assessment_start"):
            try:
                with show_loading("Generating assessment questions..."):
                    user_id = st.session_state["user_id"]
                    response = assessment_service.conduct_assessment(user_id, topic)
                
                # Store the question (simplified - in real implementation, parse the response)
                st.session_state["assessment_question"] = f"Assessment question about {topic}"
                st.session_state["assessment_topic"] = topic
                st.rerun()
                
            except Exception as e:
                handle_api_error(e, "Assessment")
    else:
        # Display question and get answer
        question = st.session_state["assessment_question"]
        answer = render_question_input(question)
        
        if st.button("Submit Answer", type="primary", key="assessment_submit"):
            if not answer:
                st.warning("Please provide an answer")
                return
            
            try:
                with show_loading("Evaluating your answer..."):
                    user_id = st.session_state["user_id"]
                    topic = st.session_state["assessment_topic"]
                    response = assessment_service.conduct_assessment(user_id, topic, answer)
                
                # Store in history
                st.session_state["assessment_history"].append({
                    "topic": topic,
                    "question": question,
                    "answer": answer,
                    "result": response
                })
                
                show_success("Assessment completed!")
                
                # Reset and get next action from backend
                st.session_state["assessment_question"] = None
                access_token = st.session_state.get("access_token")
                workflow_state = workflow_service.get_workflow_state(user_id, access_token)
                next_action = workflow_state.get("next_action", "skill_gap")
                st.session_state["next_action"] = next_action
                st.rerun()
                
            except Exception as e:
                handle_api_error(e, "Assessment")


def render_learning_stage():
    """Render learning stage."""
    st.markdown("## 🎓 Learning Roadmap")
    
    st.markdown("""
    Based on your assessment, let's generate a personalized learning roadmap to help you achieve your career goals.
    """)
    
    # Topic request
    topic_request = st.text_input(
        "What would you like to learn about?",
        placeholder="e.g., Full-stack development, Data science, Cloud architecture",
        value="Full-stack web development"
    )
    
    if st.button("Generate Roadmap", type="primary", key="learning_generate"):
        if not topic_request:
            st.warning("Please enter a topic")
            return
        
        try:
            with show_loading("Generating your personalized learning roadmap..."):
                user_id = st.session_state["user_id"]
                access_token = st.session_state["access_token"]
                response = roadmap_service.generate_roadmap(user_id, topic_request, access_token)
            
            st.session_state["learning_roadmap"] = response
            show_success("Learning roadmap generated!")
            
        except Exception as e:
            handle_api_error(e, "Learning Roadmap")
    
    # Display roadmap if available
    if st.session_state["learning_roadmap"]:
        st.markdown("---")
        st.markdown("### 📚 Your Learning Roadmap")
        
        roadmap = st.session_state["learning_roadmap"]
        if "result" in roadmap:
            result = roadmap["result"]
            if isinstance(result, dict):
                if "roadmap" in result:
                    for i, topic in enumerate(result["roadmap"], 1):
                        st.markdown(f"{i}. {topic}")
                else:
                    st.json(result)
            else:
                st.markdown(str(result))
    
    if st.button("Continue", key="learning_continue"):
        # Get next action from backend
        user_id = st.session_state["user_id"]
        access_token = st.session_state.get("access_token")
        workflow_state = workflow_service.get_workflow_state(user_id, access_token)
        next_action = workflow_state.get("next_action", "reflection")
        st.session_state["next_action"] = next_action
        st.rerun()


def render_placement_stage():
    """Render placement stage."""
    st.markdown("## 💼 Placement Readiness Assessment")
    
    st.markdown("""
    Let's assess your placement readiness across technical skills, communication, interview preparation, and resume quality.
    """)
    
    # Placement setup
    col1, col2 = st.columns(2)
    
    with col1:
        target_role = st.text_input("Target Role", placeholder="e.g., Software Engineer, Data Scientist")
    
    with col2:
        target_companies = st.text_input("Target Companies (comma-separated)", placeholder="e.g., Google, Microsoft, Amazon")
    
    st.markdown("---")
    
    if st.button("Assess Placement Readiness", type="primary", key="placement_assess"):
        if not target_role:
            st.warning("Please enter a target role")
            return
        
        companies = [c.strip() for c in target_companies.split(",")] if target_companies else []
        
        try:
            with show_loading("Assessing your placement readiness..."):
                user_id = st.session_state["user_id"]
                response = placement_service.assess_placement_readiness(user_id, target_role, companies)
            
            st.session_state["placement_assessment"] = response
            show_success("Placement assessment completed!")
            st.rerun()
            
        except Exception as e:
            handle_api_error(e, "Placement Assessment")
    
    # Display placement assessment if available
    if st.session_state.get("placement_assessment"):
        st.markdown("---")
        st.markdown("### 📊 Placement Assessment Results")
        
        assessment = st.session_state["placement_assessment"]
        
        # Status
        status = assessment.get("status", "unknown")
        status_color = {
            "ready": "🟢",
            "in_progress": "🟡",
            "needs_work": "🔴"
        }.get(status, "⚪")
        
        st.markdown(f"**Status:** {status_color} {status.upper()}")
        
        # Profile scores
        if "profile" in assessment:
            profile = assessment["profile"]
            st.markdown("### 📈 Readiness Scores")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                render_stat_card("Technical", f"{profile.get('technical_readiness', 0):.0f}%")
            
            with col2:
                render_stat_card("Communication", f"{profile.get('communication_score', 0):.0f}%")
            
            with col3:
                render_stat_card("Interview", f"{profile.get('interview_readiness', 0):.0f}%")
            
            with col4:
                render_stat_card("Resume", f"{profile.get('resume_quality', 0):.0f}%")
            
            # Visual chart for scores
            st.markdown("---")
            st.subheader("Readiness Overview")
            
            import plotly.graph_objects as go
            
            categories = ['Technical', 'Communication', 'Interview', 'Resume']
            values = [
                profile.get('technical_readiness', 0),
                profile.get('communication_score', 0),
                profile.get('interview_readiness', 0),
                profile.get('resume_quality', 0)
            ]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=categories,
                    y=values,
                    marker_color=['#1E88E5', '#43A047', '#FB8C00', '#E53935']
                )
            ])
            
            fig.update_layout(
                title="Placement Readiness Scores",
                yaxis_title="Score (%)",
                yaxis_range=[0, 100],
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        if "recommendations" in assessment and assessment["recommendations"]:
            st.markdown("---")
            st.markdown("### 💡 Recommendations")
            for i, rec in enumerate(assessment["recommendations"], 1):
                st.markdown(f"{i}. {rec}")
        
        # Next Steps
        if "next_steps" in assessment and assessment["next_steps"]:
            st.markdown("---")
            st.markdown("### 🎯 Next Steps")
            for i, step in enumerate(assessment["next_steps"], 1):
                st.markdown(f"{i}. {step}")
        
        # Timeline
        if "estimated_timeline" in assessment:
            st.markdown("---")
            st.markdown(f"### ⏱️ Estimated Timeline: {assessment['estimated_timeline']}")
        
        st.markdown("---")
        
        if st.button("Continue", key="placement_continue"):
            # Get next action from backend
            user_id = st.session_state["user_id"]
            access_token = st.session_state.get("access_token")
            workflow_state = workflow_service.get_workflow_state(user_id, access_token)
            next_action = workflow_state.get("next_action", "placement_aptitude")
            st.session_state["next_action"] = next_action
            st.rerun()


def render_interview_stage():
    """Render interview stage."""
    st.markdown("## 💼 Mock Interview")
    
    st.markdown("""
    Practice your interview skills with our AI recruiter. This will help you prepare for real job interviews.
    """)
    
    # Interview setup
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input("Target Company", placeholder="e.g., Google, Microsoft, Startup")
    
    with col2:
        job_role = st.text_input("Target Role", placeholder="e.g., Software Engineer, Data Scientist")
    
    st.markdown("---")
    
    # Interview interaction
    if "interview_question" not in st.session_state:
        st.session_state["interview_question"] = None
    
    if st.session_state["interview_question"] is None:
        if st.button("Start Interview", type="primary", key="interview_start"):
            if not company_name or not job_role:
                st.warning("Please enter company and role")
                return
            
            try:
                with show_loading("Starting interview session..."):
                    user_id = st.session_state["user_id"]
                    response = interview_service.conduct_interview(
                        user_id, company_name, job_role, "Start interview"
                    )
                
                # Store interview context
                st.session_state["interview_question"] = f"Tell me about yourself and why you want to work at {company_name} as a {job_role}?"
                st.session_state["interview_company"] = company_name
                st.session_state["interview_role"] = job_role
                st.rerun()
                
            except Exception as e:
                handle_api_error(e, "Interview")
    else:
        # Display question and get answer
        question = st.session_state["interview_question"]
        answer = render_question_input(question)
        
        if st.button("Submit Answer", type="primary", key="interview_submit"):
            if not answer:
                st.warning("Please provide an answer")
                return
            
            try:
                with show_loading("Evaluating your answer..."):
                    user_id = st.session_state["user_id"]
                    company = st.session_state["interview_company"]
                    role = st.session_state["interview_role"]
                    response = interview_service.conduct_interview(user_id, company, role, answer)
                
                # Store in history
                st.session_state["interview_history"].append({
                    "company": company,
                    "role": role,
                    "question": question,
                    "answer": answer,
                    "result": response
                })
                
                show_success("Interview session completed!")
                
                # Reset and get next action from backend
                st.session_state["interview_question"] = None
                access_token = st.session_state.get("access_token")
                workflow_state = workflow_service.get_workflow_state(user_id, access_token)
                next_action = workflow_state.get("next_action", "reflection")
                st.session_state["next_action"] = next_action
                st.rerun()
                
            except Exception as e:
                handle_api_error(e, "Interview")


def render_reflection_stage():
    """Render reflection stage."""
    st.markdown("## 🤔 Reflection")
    
    st.markdown("""
    Take a moment to reflect on your learning journey. This helps consolidate your knowledge and identify areas for improvement.
    """)
    
    reflection_prompt = st.text_area(
        "What have you learned so far? What challenges did you face? What would you like to focus on next?",
        placeholder="Share your thoughts and insights...",
        height=200
    )
    
    if st.button("Submit Reflection", type="primary", key="reflection_submit"):
        if not reflection_prompt:
            st.warning("Please share your reflection")
            return
        
        try:
            with show_loading("Processing your reflection..."):
                user_id = st.session_state["user_id"]
                response = reflection_service.conduct_reflection(user_id, reflection_prompt)
            
            # Store in history
            st.session_state["reflection_notes"].append({
                "reflection": reflection_prompt,
                "result": response
            })
            
            show_success("Reflection saved!")
            
            # Get next action from backend
            access_token = st.session_state.get("access_token")
            workflow_state = workflow_service.get_workflow_state(user_id, access_token)
            next_action = workflow_state.get("next_action", "dashboard")
            st.session_state["next_action"] = next_action
            st.rerun()
            
        except Exception as e:
            handle_api_error(e, "Reflection")


def render_skill_gap_stage():
    """Render skill gap analysis stage."""
    st.markdown("## 🔍 Skill Gap Analysis")
    
    st.markdown("""
    Analyzing your skill gaps based on assessment results to identify areas for improvement.
    """)
    
    if st.button("Analyze Skill Gaps", type="primary", key="skill_gap_analyze"):
        try:
            with show_loading("Analyzing your skill gaps..."):
                user_id = st.session_state["user_id"]
                access_token = st.session_state.get("access_token")
                response = skill_gap_service.analyze_skill_gap(user_id, access_token)
            
            st.session_state["skill_gap_result"] = response
            show_success("Skill gap analysis completed!")
            st.rerun()
        except Exception as e:
            handle_api_error(e, "Skill Gap Analysis")
    
    if st.session_state.get("skill_gap_result"):
        st.markdown("---")
        st.markdown("### 📊 Skill Gap Results")
        st.json(st.session_state["skill_gap_result"])
        
        if st.button("Continue", key="skill_gap_continue"):
            user_id = st.session_state["user_id"]
            access_token = st.session_state.get("access_token")
            workflow_state = workflow_service.get_workflow_state(user_id, access_token)
            next_action = workflow_state.get("next_action", "roadmap")
            st.session_state["next_action"] = next_action
            st.rerun()


def render_roadmap_stage():
    """Render learning roadmap stage."""
    st.markdown("## 🗺️ Learning Roadmap")
    
    st.markdown("""
    Your personalized learning roadmap based on skill gap analysis.
    """)
    
    topic_request = st.text_input(
        "What would you like to learn about?",
        placeholder="e.g., Full-stack development, Data science",
        value="Full-stack web development"
    )
    
    if st.button("Generate Roadmap", type="primary", key="roadmap_generate"):
        try:
            with show_loading("Generating your personalized learning roadmap..."):
                user_id = st.session_state["user_id"]
                access_token = st.session_state.get("access_token")
                response = roadmap_service.generate_roadmap(user_id, topic_request, access_token)
            
            st.session_state["roadmap_result"] = response
            show_success("Learning roadmap generated!")
            st.rerun()
        except Exception as e:
            handle_api_error(e, "Roadmap Generation")
    
    if st.session_state.get("roadmap_result"):
        st.markdown("---")
        st.markdown("### 📚 Your Learning Roadmap")
        st.json(st.session_state["roadmap_result"])
        
        if st.button("Continue", key="roadmap_continue"):
            user_id = st.session_state["user_id"]
            access_token = st.session_state.get("access_token")
            workflow_state = workflow_service.get_workflow_state(user_id, access_token)
            next_action = workflow_state.get("next_action", "learning")
            st.session_state["next_action"] = next_action
            st.rerun()


def render_readiness_stage():
    """Render readiness gate stage."""
    st.markdown("## 🚪 Readiness Gate")
    
    st.markdown("""
    Evaluating your readiness for placement simulation.
    """)
    
    if st.button("Evaluate Readiness", type="primary", key="readiness_evaluate"):
        try:
            with show_loading("Evaluating your placement readiness..."):
                user_id = st.session_state["user_id"]
                access_token = st.session_state.get("access_token")
                response = readiness_service.evaluate_readiness(user_id, access_token)
            
            st.session_state["readiness_result"] = response
            show_success("Readiness evaluation completed!")
            st.rerun()
        except Exception as e:
            handle_api_error(e, "Readiness Evaluation")
    
    if st.session_state.get("readiness_result"):
        st.markdown("---")
        st.markdown("### 📊 Readiness Results")
        st.json(st.session_state["readiness_result"])
        
        if st.button("Continue", key="readiness_continue"):
            user_id = st.session_state["user_id"]
            access_token = st.session_state.get("access_token")
            workflow_state = workflow_service.get_workflow_state(user_id, access_token)
            next_action = workflow_state.get("next_action", "placement_aptitude")
            st.session_state["next_action"] = next_action
            st.rerun()


def render_placement_round_stage(round_name: str, title: str, emoji: str):
    """Render a placement round stage with backend integration."""
    st.markdown(f"## {emoji} {title}")

    session_key = f"placement_{round_name}_result"
    if session_key not in st.session_state:
        st.session_state[session_key] = None

    if st.session_state[session_key] is None:
        if st.button(f"Start {title}", type="primary", key=f"placement_{round_name}_start"):
            try:
                with show_loading(f"Running {title.lower()}..."):
                    user_id = st.session_state["user_id"]
                    access_token = st.session_state.get("access_token")
                    response = placement_service.run_round(round_name, user_id, access_token)
                st.session_state[session_key] = response
                show_success(f"{title} completed!")
                st.rerun()
            except Exception as e:
                handle_api_error(e, title)
                return
        else:
            st.info(f"Click Start to begin the {title.lower()}.")
            return

    result = st.session_state[session_key]
    st.markdown("---")
    st.markdown("### Results")

    if "question" in result and result["question"]:
        question = result["question"]
        if isinstance(question, dict):
            st.markdown(f"**Question:** {question.get('question', question.get('text', 'N/A'))}")
        else:
            st.markdown(f"**Question:** {question}")

    if result.get("score") is not None:
        st.metric("Score", f"{result['score']:.0f}%")

    if result.get("strengths"):
        st.markdown("**Strengths:**")
        for s in result["strengths"]:
            st.markdown(f"- {s}")

    if result.get("weaknesses"):
        st.markdown("**Areas to Improve:**")
        for w in result["weaknesses"]:
            st.markdown(f"- {w}")

    if result.get("next_action"):
        st.info(f"Next: {format_stage_name(result['next_action'])}")

    next_stage = placement_service.NEXT_STAGE.get(round_name, "dashboard")
    if st.button("Continue", key=f"placement_{round_name}_continue"):
        st.session_state[session_key] = None
        st.session_state["current_stage"] = next_stage
        st.rerun()


def render_placement_aptitude_stage():
    render_placement_round_stage("aptitude", "Placement Aptitude Round", "🧠")


def render_placement_coding_stage():
    render_placement_round_stage("coding", "Placement Coding Round", "💻")


def render_placement_technical_stage():
    render_placement_round_stage("technical", "Placement Technical Round", "⚙️")


def render_placement_interview_stage():
    render_placement_round_stage("interview", "Placement Interview Round", "🎤")


def render_placement_hr_stage():
    render_placement_round_stage("hr", "Placement HR Round", "👥")


def render_placement_report_stage():
    render_placement_round_stage("report", "Placement Report", "📄")


def render_career_intelligence_stage():
    """Render career intelligence stage."""
    st.markdown("## 🧠 Career Intelligence")

    if "career_intelligence_data" not in st.session_state:
        st.session_state["career_intelligence_data"] = None

    if st.session_state["career_intelligence_data"] is None:
        try:
            with show_loading("Loading career intelligence..."):
                user_id = st.session_state["user_id"]
                access_token = st.session_state.get("access_token")
                data = career_intelligence_service.get_intelligence(user_id, access_token)
            st.session_state["career_intelligence_data"] = data
        except Exception as e:
            handle_api_error(e, "Career Intelligence")
            return

    data = st.session_state["career_intelligence_data"]

    col1, col2, col3 = st.columns(3)
    with col1:
        render_stat_card("Readiness", format_readiness_score(data.get("readiness", 0) * 100))
    with col2:
        render_stat_card("Confidence", f"{data.get('confidence', 0) * 100:.0f}%")
    with col3:
        render_stat_card("Next Action", format_stage_name(data.get("next_best_action", "dashboard")))

    st.markdown("---")

    if data.get("profile"):
        st.markdown("### Profile")
        profile = data["profile"]
        st.markdown(f"- **Career Goal:** {profile.get('career_goal', 'Not set')}")
        st.markdown(f"- **Experience:** {profile.get('experience_level', 'Not set')}")

    if data.get("skills"):
        st.markdown("### Skills")
        for skill, score in data["skills"].items():
            st.progress(min(score / 100.0, 1.0), text=f"{skill}: {score}")

    if data.get("skill_gaps"):
        st.markdown("### Skill Gaps")
        render_recommendations(data["skill_gaps"])

    if data.get("recommendations"):
        st.markdown("### Recommendations")
        render_recommendations(data["recommendations"])

    if st.button("Refresh", key="career_intelligence_refresh"):
        st.session_state["career_intelligence_data"] = None
        st.rerun()

    if st.button("Continue to Dashboard", key="career_intelligence_continue"):
        st.session_state["career_intelligence_data"] = None
        st.session_state["current_stage"] = "dashboard"
        st.rerun()


def render_dashboard_stage():
    """Render dashboard stage."""
    st.markdown("## 📊 Your Career Dashboard")
    
    st.markdown("Loading your dashboard data...")
    
    try:
        with show_loading("Loading dashboard..."):
            user_id = st.session_state["user_id"]
            access_token = st.session_state["access_token"]
            dashboard_data = dashboard_service.get_dashboard(user_id, access_token)
        
        st.session_state["dashboard_data"] = dashboard_data
        
        # Display dashboard content
        st.markdown("---")
        
        # User info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            render_stat_card("Name", dashboard_data.get("name", "N/A"))
        
        with col2:
            render_stat_card("Career Goal", dashboard_data.get("career_goal", "Not set"))
        
        with col3:
            readiness = dashboard_data.get("readiness_score", 0)
            render_stat_card("Readiness", format_readiness_score(readiness))
        
        st.markdown("---")
        
        # Readiness chart
        st.subheader("📈 Readiness Score")
        render_readiness_chart(dashboard_data.get("readiness_score", 0))
        
        st.markdown("---")
        
        # Learning progress
        if "roadmap" in dashboard_data and "completed_topics" in dashboard_data:
            st.subheader("📚 Learning Progress")
            render_progress_chart(dashboard_data["roadmap"], dashboard_data["completed_topics"])
        
        st.markdown("---")
        
        # Recommendations
        if "recommendations" in dashboard_data:
            render_recommendations(dashboard_data["recommendations"])
        
        st.markdown("---")
        
        # Activity history
        st.subheader("📋 Recent Activity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Assessment History")
            if dashboard_data.get("assessment_history"):
                for i, assessment in enumerate(dashboard_data["assessment_history"][-3:], 1):
                    st.markdown(f"{i}. {assessment.get('topic', 'Unknown')}")
            else:
                st.caption("No assessments yet")
        
        with col2:
            st.markdown("### Interview History")
            if dashboard_data.get("interview_history"):
                for i, interview in enumerate(dashboard_data["interview_history"][-3:], 1):
                    st.markdown(f"{i}. {interview.get('role', 'Unknown')}")
            else:
                st.caption("No interviews yet")
        
        st.markdown("---")
        
        # Action buttons - use backend next action
        if st.button("Continue", key="dashboard_continue"):
            # Get next action from backend
            workflow_state = workflow_service.get_workflow_state(user_id, access_token)
            next_action = workflow_state.get("next_action", "dashboard")
            if next_action == "dashboard":
                # If backend says stay on dashboard, check if there's a specific skill to continue
                next_action = workflow_state.get("current_skill", "dashboard")
            st.session_state["next_action"] = next_action
            st.rerun()
        
    except Exception as e:
        handle_api_error(e, "Dashboard")


if __name__ == "__main__":
    main()
