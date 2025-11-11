"""
Application settings loaded from environment variables.
Uses pydantic-settings for validation and type safety.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # OpenAI API Configuration
    OPENAI_API_KEY: str
    
    # Environment Configuration
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "DEBUG"
    
    # Database Configuration
    SQLITE_DATABASE_PATH: str = "../data/sqlite/memorychat.db"
    CHROMADB_PATH: str = "../data/chromadb"
    
    # API Configuration
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create a singleton instance
settings = Settings()

