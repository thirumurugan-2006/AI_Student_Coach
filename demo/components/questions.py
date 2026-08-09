"""
Question Input Component for Streamlit Demo Frontend.
"""

import streamlit as st


def render_question_input(question: str, placeholder: str = "Type your answer here...") -> str:
    """
    Render a question input field.
    
    Args:
        question: Question text
        placeholder: Input placeholder text
        
    Returns:
        User's answer
    """
    st.markdown(f"### ❓ {question}")
    answer = st.text_area(
        "Your Answer",
        placeholder=placeholder,
        height=150,
        key=f"question_input_{hash(question)}"
    )
    return answer


def render_multiple_choice(question: str, options: list, question_id: str = None) -> str:
    """
    Render a multiple choice question with radio buttons.
    
    Args:
        question: Question text
        options: List of options
        question_id: Optional question ID for tracking
        
    Returns:
        Selected option
    """
    st.markdown(f"### ❓ {question}")
    
    # Display options with letter labels
    option_labels = ["A", "B", "C", "D"]
    labeled_options = [f"{label}. {option}" for label, option in zip(option_labels, options)]
    
    selected_labeled = st.radio(
        "Select your answer:",
        labeled_options,
        key=f"multiple_choice_{question_id or hash(question)}"
    )
    
    # Return the original option text
    if selected_labeled:
        for label, option in zip(option_labels, options):
            if selected_labeled.startswith(f"{label}."):
                return option
    return selected_labeled


def render_coding_question(question_data: dict) -> dict:
    """
    Render a coding question with problem statement and code input.
    
    Args:
        question_data: Dictionary with question details including:
            - question: Problem statement
            - input_format: Input format description
            - output_format: Output format description
            - constraints: Constraints
            - examples: Example test cases
            - question_id: Question ID
            
    Returns:
        User's code solution
    """
    st.markdown("### 💻 Coding Problem")
    
    # Problem statement
    st.markdown(f"**Problem:** {question_data.get('question', '')}")
    
    # Input/Output format
    if question_data.get('input_format'):
        st.markdown(f"**Input Format:** {question_data['input_format']}")
    
    if question_data.get('output_format'):
        st.markdown(f"**Output Format:** {question_data['output_format']}")
    
    # Constraints
    if question_data.get('constraints'):
        st.markdown(f"**Constraints:** {question_data['constraints']}")
    
    # Examples
    if question_data.get('examples'):
        st.markdown("**Examples:**")
        for i, example in enumerate(question_data['examples'], 1):
            st.markdown(f"Example {i}:")
            st.code(example, language="text")
    
    st.markdown("---")
    
    # Code input
    code = st.text_area(
        "Your Solution",
        placeholder="# Write your code here...",
        height=300,
        key=f"coding_{question_data.get('question_id', hash(question_data.get('question', '')))}"
    )
    
    return code


def render_interview_question(question_data: dict) -> str:
    """
    Render an interview question with context.
    
    Args:
        question_data: Dictionary with question details including:
            - question: Interview question
            - context: Additional context (company, role, etc.)
            - question_id: Question ID
            
    Returns:
        User's answer
    """
    st.markdown("### 🎤 Interview Question")
    
    # Display context if available
    if question_data.get('context'):
        st.info(f"Context: {question_data['context']}")
    
    # Display question
    st.markdown(f"**Question:** {question_data.get('question', '')}")
    
    st.markdown("---")
    
    # Answer input
    answer = st.text_area(
        "Your Answer",
        placeholder="Type your response...",
        height=200,
        key=f"interview_{question_data.get('question_id', hash(question_data.get('question', '')))}"
    )
    
    return answer


def render_question_header(skill: str, topic: str = None, difficulty: str = None, progress: str = None):
    """
    Render question header with metadata.
    
    Args:
        skill: Skill name
        topic: Optional topic
        difficulty: Optional difficulty level
        progress: Optional progress string
    """
    if progress:
        st.markdown(f"**Progress:** {progress}")
    
    st.markdown(f"**Skill:** {skill}")
    
    if topic:
        st.markdown(f"**Topic:** {topic}")
    
    if difficulty:
        difficulty_emoji = {
            "easy": "🟢",
            "medium": "🟡",
            "hard": "🔴"
        }.get(difficulty.lower(), "")
        st.markdown(f"**Difficulty:** {difficulty_emoji} {difficulty.title()}")
    
    st.markdown("---")
