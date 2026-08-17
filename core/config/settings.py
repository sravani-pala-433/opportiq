from functools import lru_cache
from pydantic_settings import BaseSettings
from core.logging import get_logger

logger = get_logger(__name__)

logger.info("Initializing settings")
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY : str
    DB_USER : str
    DB_PASSWORD : str
    DB_HOST : str
    DB_NAME : str
    TEST_DB_NAME : str

    # Google OAuth 2.0 Configuration
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

