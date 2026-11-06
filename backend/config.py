"""Configuration settings for AI Bug Triage & Resolution Team."""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Bug Triage & Resolution Team"
    VERSION: str = "1.0.0"
    # Connection credentials must come from the environment or an untracked .env file.
    # Empty values intentionally leave Switch delivery disabled instead of attempting a
    # login with a repository-visible fallback credential.
    SWITCH_API_URL: str = os.getenv("SWITCH_API_URL", "")
    SWITCH_ADMIN_EMAIL: str = os.getenv("SWITCH_ADMIN_EMAIL", "")
    SWITCH_ADMIN_PASSWORD: str = os.getenv("SWITCH_ADMIN_PASSWORD", "")
    SWITCH_AGENT_ID: str = os.getenv("SWITCH_AGENT_ID", "")
    SWITCH_AGENT_API_KEY: str = os.getenv("SWITCH_AGENT_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bugtriage.db")
    SAMPLE_APP_PATH: str = os.getenv("SAMPLE_APP_PATH", "./demo/sample_app")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SWITCH_ROOM_NAME: str = "ai-bug-triage"

settings = Settings()
