"""
Configuration management for the FastAPI application.
"""
import os
from typing import Optional
from pydantic import BaseSettings, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = "LLM Query-Retrieval System"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database settings
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str
    postgres_db: str
    
    # Pinecone settings
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str
    
    # OpenAI settings
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 1500
    openai_temperature: float = 0.1
    
    # Embedding model settings
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Security settings
    secret_key: Optional[str] = None
    allowed_hosts: str = "localhost,127.0.0.1"
    
    # Rate limiting
    rate_limit_requests_per_minute: int = 100
    
    # Optional services
    redis_url: Optional[str] = None
    sentry_dsn: Optional[str] = None
    
    @validator('allowed_hosts')
    def parse_allowed_hosts(cls, v):
        """Parse comma-separated allowed hosts."""
        return [host.strip() for host in v.split(',')]
    
    @property
    def database_url(self) -> str:
        """Construct database URL."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
