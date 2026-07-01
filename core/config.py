"""
core/config.py — Load & validasi environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env dari root project
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    # App
    APP_NAME: str = os.getenv("APP_NAME", "DataBuddy")
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # LLM
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Database lokal
    LOCAL_DB_PATH: Path = BASE_DIR / os.getenv("LOCAL_DB_PATH", "data/local.db")

    # Upload
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "200"))

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def has_supabase(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)

    @property
    def has_gemini(self) -> bool:
        return bool(self.GEMINI_API_KEY)

    @property
    def has_openai(self) -> bool:
        return bool(self.OPENAI_API_KEY)


# Singleton config
config = Config()
