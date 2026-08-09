"""
Student Memory Engine

Stores everything the AI knows about a student.

Every skill reads from here.

Every skill writes back here.

Persists to database via repositories.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.user_repository import UserRepository
from repositories.student_repository import StudentRepository, StudentUpdate


class StudentMemory:

    def __init__(self):
        # In-memory cache for performance
        self.students = {}
        
        # Repositories for database persistence
        self.user_repo = UserRepository()
        self.student_repo = StudentRepository()

    # -----------------------------------------------------
    # Create Student
    # -----------------------------------------------------

    def create_student(self, student_id: str, name: str):

        self.students[student_id] = {

            "id": student_id,

            "name": name,

            "created_at": datetime.now(),

            # -----------------------------
            # Career Profile
            # -----------------------------

            "career_goal": None,

            "target_company": None,

            "experience_level": None,

            "study_hours": 0,

            "learning_style": None,

            # -----------------------------
            # Skills
            # -----------------------------

            "skills": {},

            "knowledge_graph": {},

            # -----------------------------
            # Progress
            # -----------------------------

            "roadmap": [],

            "completed_topics": [],

            "weak_topics": [],

            "strong_topics": [],

            # -----------------------------
            # Assessments
            # -----------------------------

            "assessment_history": [],

            # -----------------------------
            # Interviews
            # -----------------------------

            "interview_history": [],

            "recruiter_feedback": [],

            # -----------------------------
            # Reflection
            # -----------------------------

            "reflection_notes": [],

            # -----------------------------
            # Readiness
            # -----------------------------

            "readiness_score": 0,

            # -----------------------------
            # Placement
            # -----------------------------

            "placement_history": [],

            # -----------------------------
            # Flags
            # -----------------------------

            "survey_completed": False,

            "assessment_completed": False,

            "interview_completed": False
        }

    async def initialize_student(self, db: AsyncSession, user_id: str, name: str = "New User"):
        """
        Initialize student memory for a new user.
        This is called automatically after registration.
        Loads from database if exists, creates new profile if not.
        """
        # Try to load from database first
        student_profile = await self.student_repo.get_by_user_id(db, user_id)
        
        if student_profile:
            # Load existing profile from database
            self.students[user_id] = {
                "id": user_id,
                "name": name,
                "created_at": student_profile.created_at,
                "career_goal": student_profile.career_goal,
                "target_company": student_profile.target_company,
                "experience_level": student_profile.experience_level,
                "study_hours": student_profile.study_hours or 0,
                "learning_style": student_profile.learning_style,
                "skills": student_profile.skills or {},
                "knowledge_graph": student_profile.knowledge_graph or {},
                "roadmap": student_profile.roadmap or [],
                "completed_topics": student_profile.completed_topics or [],
                "weak_topics": student_profile.weak_topics or [],
                "strong_topics": student_profile.strong_topics or [],
                "assessment_history": [],
                "interview_history": [],
                "recruiter_feedback": [],
                "reflection_notes": [],
                "placement_history": [],
                "readiness_score": student_profile.readiness_score or 0,
                "survey_completed": False,
                "assessment_completed": False,
                "interview_completed": False
            }
        else:
            # Create new in-memory profile
            self.create_student(user_id, name)
        
        return self.students[user_id]

    # -----------------------------------------------------

    def get_profile(self, student_id):

        return self.students.get(student_id)

    # -----------------------------------------------------

    def get_profile_summary(self, student_id: str = None) -> str:
        """
        Returns a string summary of the current student profile.
        Used by BaseSkill to build prompts.
        """
        if student_id and student_id in self.students:
            profile = self.students[student_id]
            summary = f"Student ID: {profile.get('id', 'Unknown')}\n"
            summary += f"Name: {profile.get('name', 'Unknown')}\n"
            summary += f"Career Goal: {profile.get('career_goal', 'Not specified')}\n"
            summary += f"Experience Level: {profile.get('experience_level', 'Not specified')}\n"
            summary += f"Learning Style: {profile.get('learning_style', 'Not specified')}\n"
            summary += f"Study Hours: {profile.get('study_hours', 0)}\n"
            summary += f"Skills: {profile.get('skills', {})}\n"
            summary += f"Survey Completed: {profile.get('survey_completed', False)}\n"
            summary += f"Assessment Completed: {profile.get('assessment_completed', False)}\n"
            summary += f"Interview Completed: {profile.get('interview_completed', False)}\n"
            summary += f"Readiness Score: {profile.get('readiness_score', 0)}\n"
            summary += f"Placement Rounds: {len(profile.get('placement_history', []))}\n"
            return summary
        return "No student profile available. Student needs to be initialized."

    # -----------------------------------------------------

    async def save(self, db: AsyncSession, student_id: str):
        """
        Persist student memory to database.
        """
        if student_id not in self.students:
            return
        
        profile = self.students[student_id]
        
        # Update student profile in database
        update_data = StudentUpdate(
            career_goal=profile.get("career_goal"),
            target_company=profile.get("target_company"),
            experience_level=profile.get("experience_level"),
            study_hours=profile.get("study_hours"),
            learning_style=profile.get("learning_style"),
            skills=profile.get("skills"),
            knowledge_graph=profile.get("knowledge_graph"),
            roadmap=profile.get("roadmap"),
            completed_topics=profile.get("completed_topics"),
            weak_topics=profile.get("weak_topics"),
            strong_topics=profile.get("strong_topics"),
            readiness_score=profile.get("readiness_score")
        )
        
        await self.student_repo.update_student_profile(db, student_id, update_data)

    # -----------------------------------------------------

    def update_from_survey(self, student_id: str, profile_data: dict) -> None:
        """
        Updates student profile from survey results.
        """
        if student_id not in self.students:
            self.create_student(student_id, profile_data.get("name", "Unknown"))
        
        profile = self.students[student_id]
        
        # Update career-related fields
        if "career_goal" in profile_data:
            profile["career_goal"] = profile_data["career_goal"]
        if "target_company" in profile_data:
            profile["target_company"] = profile_data["target_company"]
        if "experience_level" in profile_data:
            profile["experience_level"] = profile_data["experience_level"]
        if "learning_style" in profile_data:
            profile["learning_style"] = profile_data["learning_style"]
        
        # Mark survey as completed
        profile["survey_completed"] = True

    # -----------------------------------------------------
    # Career Goal
    # -----------------------------------------------------

    def update_goal(self, student_id, goal):

        self.students[student_id]["career_goal"] = goal

    # -----------------------------------------------------
    # Skills
    # -----------------------------------------------------

    def update_skill(self,
                     student_id,
                     skill_name,
                     score):

        self.students[student_id]["skills"][skill_name] = score

    # -----------------------------------------------------
    # Knowledge Graph
    # -----------------------------------------------------

    def update_concept(self,
                       student_id,
                       topic,
                       concept,
                       status):

        graph = self.students[student_id]["knowledge_graph"]

        if topic not in graph:

            graph[topic] = {}

        graph[topic][concept] = status

    # -----------------------------------------------------
    # Weak Topic
    # -----------------------------------------------------

    def add_weak_topic(self,
                       student_id,
                       topic):

        profile = self.students[student_id]

        if topic not in profile["weak_topics"]:

            profile["weak_topics"].append(topic)

    # -----------------------------------------------------
    # Strong Topic
    # -----------------------------------------------------

    def add_strong_topic(self,
                         student_id,
                         topic):

        profile = self.students[student_id]

        if topic not in profile["strong_topics"]:

            profile["strong_topics"].append(topic)

    # -----------------------------------------------------
    # Roadmap
    # -----------------------------------------------------

    def update_roadmap(
            self,
            student_id,
            roadmap):

        self.students[student_id]["roadmap"] = roadmap

    # -----------------------------------------------------
    # Assessment
    # -----------------------------------------------------

    def add_assessment(self,
                       student_id,
                       assessment):

        self.students[student_id]["assessment_history"].append(
            assessment
        )

    # -----------------------------------------------------
    # Interview
    # -----------------------------------------------------

    def add_interview(
            self,
            student_id,
            interview):

        self.students[student_id]["interview_history"].append(
            interview
        )

    # -----------------------------------------------------
    # Reflection
    # -----------------------------------------------------

    def add_reflection(
            self,
            student_id,
            note):

        self.students[student_id]["reflection_notes"].append(
            note
        )

    # -----------------------------------------------------
    # Recruiter Feedback
    # -----------------------------------------------------

    def add_feedback(
            self,
            student_id,
            feedback):

        self.students[student_id]["recruiter_feedback"].append(
            feedback
        )

    # -----------------------------------------------------
    # Readiness
    # -----------------------------------------------------

    def calculate_readiness(
            self,
            student_id):

        profile = self.students[student_id]

        if len(profile["skills"]) == 0:
            return 0

        total = sum(profile["skills"].values())

        score = total / len(profile["skills"])

        profile["readiness_score"] = round(score)

        return round(score)