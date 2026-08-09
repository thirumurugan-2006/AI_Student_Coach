from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """
    Application configuration settings.
    Uses Pydantic v2 BaseSettings to load from environment variables or .env file.
    """

    # --------------------------------------------------------------------------
    # Application
    # --------------------------------------------------------------------------
    PROJECT_NAME: str = "AI-Native Personalized Career Coach"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # --------------------------------------------------------------------------
    # Database
    # --------------------------------------------------------------------------
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/career_coach.db"

    # --------------------------------------------------------------------------
    # Security / JWT
    # --------------------------------------------------------------------------
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --------------------------------------------------------------------------
    # CORS
    # --------------------------------------------------------------------------
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "*"]

    # --------------------------------------------------------------------------
    # LLM Provider Configuration
    # --------------------------------------------------------------------------
    LLM_PROVIDER: str = "groq"

    # --------------------------------------------------------------------------
    # Groq LLM (Content Generation)
    # --------------------------------------------------------------------------
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TIMEOUT: int = 60
    GROQ_TEMPERATURE: float = 0.3
    GROQ_TOP_P: float = 0.9
    GROQ_MAX_TOKENS: int = 2048

    # --------------------------------------------------------------------------
    # Ollama LLM (Planning/Reasoning)
    # --------------------------------------------------------------------------
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:4b"
    OLLAMA_TIMEOUT: int = 120

    # --------------------------------------------------------------------------
    # File Uploads
    # --------------------------------------------------------------------------
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_RESUME_TYPES: List[str] = ["application/pdf", "application/msword",
                                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
