from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for backend
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
DEFAULT_DB_PATH = BASE_DIR / "complaints.db"

class Settings(BaseSettings):
    GROQ_API_KEY: str = "your_groq_api_key_here"
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"

    model_config = SettingsConfigDict(
        env_file=(str(ENV_FILE), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
