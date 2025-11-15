"""
Application settings loaded from environment variables.
Uses pydantic-settings for validation and type safety.
"""
from pydantic import Field, field_validator
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
    
    # Memory Management - Using Mem0
    # Replaced ChromaDB with Mem0's integrated solution
    MEM0_API_KEY: str = Field(..., description="Mem0 API key for memory management")
    MEM0_ORGANIZATION_ID: str = Field(..., description="Mem0 organization ID")
    MEM0_PROJECT_ID: str = Field(..., description="Mem0 project ID")
    QDRANT_PATH: str = Field(default="../data/qdrant", description="Path to Qdrant vector database")
    QDRANT_HOST: str = Field(default="localhost", description="Qdrant server host")
    QDRANT_PORT: int = Field(default=6333, description="Qdrant server port")
    
    # API Configuration
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    
    @field_validator('MEM0_API_KEY', 'MEM0_ORGANIZATION_ID', 'MEM0_PROJECT_ID')
    @classmethod
    def validate_mem0_required_fields(cls, v: str) -> str:
        """Validate that required Mem0 fields are not placeholder values."""
        if not v or v in ['your-mem0-api-key-here', 'your-org-id-here', 'your-project-id-here']:
            raise ValueError(
                f"Mem0 configuration field must be set to a real value, not a placeholder. "
                f"Please update your .env file with actual Mem0 credentials."
            )
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create a singleton instance
settings = Settings()

