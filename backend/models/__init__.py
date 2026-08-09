"""Models package — SQLAlchemy ORM models."""

# Import all ORM models so that SQLAlchemy metadata is populated.
# Using the actual class names from each model file.
from models.user import UserModel
from models.student import StudentProfileModel
from models.readiness import ReadinessScoreModel
from models.memory import InterviewHistoryModel, ReflectionHistoryModel
from models.placement import (
    PlacementSimulationModel,
    PlacementRoundModel,
    PlacementQuestionModel,
    PlacementEvaluationModel,
    PlacementReportModel,
)
from models.question import QuestionModel, QuestionAttemptModel

# Import remaining models (class names discovered from their files)
import models.survey          # noqa: F401
import models.assessment      # noqa: F401
import models.interview       # noqa: F401
import models.learning_roadmap  # noqa: F401
import models.reflection      # noqa: F401
import models.progress        # noqa: F401
import models.resume          # noqa: F401
import models.project         # noqa: F401
import models.notification    # noqa: F401

__all__ = [
    "UserModel",
    "StudentProfileModel",
    "ReadinessScoreModel",
    "InterviewHistoryModel",
    "ReflectionHistoryModel",
    "PlacementSimulationModel",
    "PlacementRoundModel",
    "PlacementQuestionModel",
    "PlacementEvaluationModel",
    "PlacementReportModel",
    "QuestionModel",
    "QuestionAttemptModel",
]
