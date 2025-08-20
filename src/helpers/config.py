from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application Configuration
    APP_NAME: str
    APP_VERSION: str
    
    # API Keys
    GEMINI_API_KEY: str
    GENIUS_API_KEY: str
    
    # Genius API Configuration
    GENIUS_BASE_URL: str = "https://api.genius.com"
    GENIUS_CLIENT_ID: Optional[str] = None
    GENIUS_CLIENT_SECRET: Optional[str] = None
    
    # Default settings for Genius API 
    GENIUS_TIMEOUT: int = 30
    GENIUS_RETRY_ATTEMPTS: int = 3
    GENIUS_MAX_SEARCH_RESULTS: int = 10
    GENIUS_REQUEST_DELAY: int = 1
    GENIUS_USER_AGENT: str = "MusicStoryTeller/1.0"

    # Gemini API Configuration
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"
    GEMINI_TIMEOUT: int = 30
    GEMINI_RETRY_ATTEMPTS: int = 3
    GEMINI_MAX_TOKENS: int = 1024
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_TOP_P: float = 0.9

    class Config:
        env_file = ".env"
        case_sensitive = True

def get_settings() -> Settings:
    return Settings()