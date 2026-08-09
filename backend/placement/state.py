"""
Placement State

Tracks the state of an ongoing placement simulation.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone


class PlacementState:
    """
    Tracks the state of a placement simulation for a student.
    """

    def __init__(self, student_id: str):
        self.student_id = student_id
        self.simulation_id: Optional[str] = None
        self.current_round: Optional[str] = None
        self.rounds_completed = []
        self.round_results = {}
        self.overall_score = 0.0
        self.status = "not_started"
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def start(self, simulation_id: str, first_round: str):
        """Start a new simulation."""
        self.simulation_id = simulation_id
        self.current_round = first_round
        self.status = "started"
        self.started_at = datetime.now(timezone.utc)

    def complete_round(self, round_type: str, result: Dict[str, Any]):
        """Mark a round as completed."""
        self.rounds_completed.append(round_type)
        self.round_results[round_type] = result

        # Advance to next round
        from placement.simulator import PlacementSimulator
        current_index = PlacementSimulator.ROUNDS.index(round_type)
        if current_index + 1 < len(PlacementSimulator.ROUNDS):
            self.current_round = PlacementSimulator.ROUNDS[current_index + 1]
        else:
            self.current_round = None

    def complete_simulation(self, overall_score: float):
        """Mark the simulation as completed."""
        self.status = "completed"
        self.overall_score = overall_score
        self.completed_at = datetime.now(timezone.utc)
        self.current_round = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "student_id": self.student_id,
            "simulation_id": self.simulation_id,
            "current_round": self.current_round,
            "rounds_completed": self.rounds_completed,
            "round_results": self.round_results,
            "overall_score": self.overall_score,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
