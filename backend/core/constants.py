"""
Application-wide constants.

All magic strings, thresholds, and enums live here.
Never hardcode these values in business logic.
"""

# --------------------------------------------------------------------------
# Skill Names
# --------------------------------------------------------------------------

SKILL_SURVEY = "survey"
SKILL_ASSESSMENT = "assessment"
SKILL_LEARNING = "learning"
SKILL_INTERVIEW = "interview"
SKILL_REFLECTION = "reflection"
SKILL_PLACEMENT_APTITUDE = "placement.aptitude"
SKILL_PLACEMENT_CODING = "placement.coding"
SKILL_PLACEMENT_TECHNICAL = "placement.technical"
SKILL_PLACEMENT_INTERVIEW = "placement.interview"
SKILL_PLACEMENT_HR = "placement.hr"

ALL_SKILLS = [
    SKILL_SURVEY,
    SKILL_ASSESSMENT,
    SKILL_LEARNING,
    SKILL_INTERVIEW,
    SKILL_REFLECTION,
]

# --------------------------------------------------------------------------
# Experience Levels
# --------------------------------------------------------------------------

EXPERIENCE_BEGINNER = "beginner"
EXPERIENCE_INTERMEDIATE = "intermediate"
EXPERIENCE_ADVANCED = "advanced"
EXPERIENCE_EXPERT = "expert"

EXPERIENCE_LEVELS = [
    EXPERIENCE_BEGINNER,
    EXPERIENCE_INTERMEDIATE,
    EXPERIENCE_ADVANCED,
    EXPERIENCE_EXPERT,
]

# --------------------------------------------------------------------------
# Learning Styles
# --------------------------------------------------------------------------

LEARNING_VISUAL = "visual"
LEARNING_READING = "reading"
LEARNING_HANDS_ON = "hands-on"
LEARNING_AUDITORY = "auditory"

LEARNING_STYLES = [
    LEARNING_VISUAL,
    LEARNING_READING,
    LEARNING_HANDS_ON,
    LEARNING_AUDITORY,
]

# --------------------------------------------------------------------------
# Readiness Thresholds
# --------------------------------------------------------------------------

READINESS_READY_THRESHOLD = 75.0       # Score >= 75 → "Job Ready"
READINESS_PROGRESSING_THRESHOLD = 50.0  # Score >= 50 → "Progressing"
READINESS_NEEDS_WORK_THRESHOLD = 25.0   # Score >= 25 → "Needs Work"

READINESS_STATUS_READY = "job_ready"
READINESS_STATUS_PROGRESSING = "progressing"
READINESS_STATUS_NEEDS_WORK = "needs_work"
READINESS_STATUS_STARTING = "just_starting"

# --------------------------------------------------------------------------
# Difficulty Levels
# --------------------------------------------------------------------------

DIFFICULTY_EASY = "easy"
DIFFICULTY_MEDIUM = "medium"
DIFFICULTY_HARD = "hard"

DIFFICULTY_LEVELS = [DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD]

# --------------------------------------------------------------------------
# Assessment Topic Status
# --------------------------------------------------------------------------

TOPIC_STATUS_MASTERED = "mastered"
TOPIC_STATUS_PROFICIENT = "proficient"
TOPIC_STATUS_LEARNING = "learning"
TOPIC_STATUS_WEAK = "weak"
TOPIC_STATUS_NOT_STARTED = "not_started"

# --------------------------------------------------------------------------
# Score Weights for Readiness Calculation
# --------------------------------------------------------------------------

WEIGHT_TECHNICAL_SKILLS = 0.40
WEIGHT_INTERVIEW_PERFORMANCE = 0.30
WEIGHT_CONFIDENCE = 0.20
WEIGHT_ROADMAP_COMPLETION = 0.10

# --------------------------------------------------------------------------
# Token & Auth
# --------------------------------------------------------------------------

TOKEN_TYPE = "bearer"
AUTH_HEADER_TYPE = "Bearer"

# --------------------------------------------------------------------------
# API Tags
# --------------------------------------------------------------------------

TAG_USER = "User"
TAG_SURVEY = "Career Survey"
TAG_ASSESSMENT = "Assessment"
TAG_LEARNING = "Learning"
TAG_INTERVIEW = "Interview"
TAG_REFLECTION = "Reflection"
TAG_DASHBOARD = "Dashboard"
TAG_CAREER_COACH = "Career Coach"
TAG_HEALTH = "Health"

# --------------------------------------------------------------------------
# Pagination Defaults
# --------------------------------------------------------------------------

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# --------------------------------------------------------------------------
# LLM / Groq
# --------------------------------------------------------------------------

DEFAULT_LLM_MODEL = "llama3-8b-8192"
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0
RETRY_MAX_DELAY = 10.0

# --------------------------------------------------------------------------
# File Upload
# --------------------------------------------------------------------------

UPLOAD_RESUMES_SUBDIR = "resumes"
UPLOAD_CERTIFICATES_SUBDIR = "certificates"
UPLOAD_PROFILE_SUBDIR = "profile"
UPLOAD_PROJECTS_SUBDIR = "projects"
UPLOAD_REPORTS_SUBDIR = "reports"
UPLOAD_TEMP_SUBDIR = "temp"

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
