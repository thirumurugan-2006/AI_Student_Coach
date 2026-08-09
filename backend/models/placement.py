from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Float, Integer
from datetime import datetime, timezone
from database.base import Base
import uuid


class PlacementSimulationModel(Base):
    """
    SQLAlchemy model for a Placement Simulation session.
    """
    __tablename__ = "placement_simulations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), nullable=False)
    status = Column(String, default="started")
    current_round = Column(String, nullable=True)
    overall_score = Column(Float, default=0.0)
    readiness_score = Column(Float, default=0.0)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)


class PlacementRoundModel(Base):
    """
    SQLAlchemy model for a single round within a placement simulation.
    """
    __tablename__ = "placement_rounds"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    simulation_id = Column(String, ForeignKey("placement_simulations.id"), nullable=False)
    round_type = Column(String, nullable=False)
    score = Column(Float, default=0.0)
    feedback = Column(JSON, default=dict)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)


class PlacementQuestionModel(Base):
    """
    SQLAlchemy model for questions asked during a placement round.
    """
    __tablename__ = "placement_questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    round_id = Column(String, ForeignKey("placement_rounds.id"), nullable=False)
    question_text = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    options = Column(JSON, default=list)
    correct_answer = Column(String, nullable=True)
    student_answer = Column(String, nullable=True)
    is_correct = Column(String, nullable=True)


class PlacementEvaluationModel(Base):
    """
    SQLAlchemy model for evaluation results of a placement round.
    """
    __tablename__ = "placement_evaluations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    simulation_id = Column(String, ForeignKey("placement_simulations.id"), nullable=False)
    round_type = Column(String, nullable=False)
    score = Column(Float, default=0.0)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    topics = Column(JSON, default=list)
    difficulty = Column(String, nullable=True)
    performance = Column(String, nullable=True)
    feedback = Column(String, nullable=True)
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PlacementReportModel(Base):
    """
    SQLAlchemy model for the final placement report.
    """
    __tablename__ = "placement_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    simulation_id = Column(String, ForeignKey("placement_simulations.id"), nullable=False, unique=True)
    student_id = Column(String, ForeignKey("student_profiles.user_id"), nullable=False)
    overall_score = Column(Float, default=0.0)
    round_scores = Column(JSON, default=dict)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    next_best_action = Column(String, nullable=True)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
