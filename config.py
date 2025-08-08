"""
Configuration file for the LLM Query-Retrieval System.
This file contains all environment variables and API configurations.
"""

import os
from typing import Optional

# Database Configuration
POSTGRES_HOST="localhost"
POSTGRES_PORT=5432
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="password"
POSTGRES_DB="query_retrieval_db"

# Pinecone Configuration
PINECONE_ENVIRONMENT = "your_pinecone_environment"
PINECONE_API_KEY= "pcsk_4SkS38_NvWQ1EzKgz9fc6jv8uo97VSxhcydq8WVVeMVwYE7sgSCerVyTyrSyjKhYjX4URE"
PINECONE_INDEX_NAME= "your_pinecone_index_name"

# Google Gemini Configuration
GEMINI_API_KEY="AIzaSyC3eV4lBPsNL2bgHQJnJm8mNKg-hW-QQ9o"
GEMINI_MODEL="gemini-2.5-pro"
GEMINI_MAX_TOKENS=15000
GEMINI_TEMPERATURE=0.1

# Embedding Model Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Application Configuration
APP_ENV = "development"
LOG_LEVEL = "INFO"
DEBUG = True

# Security (Optional)
SECRET_KEY = "your_secret_key_here"
ALLOWED_HOSTS = "localhost,127.0.0.1"

# Rate Limiting (Optional)
RATE_LIMIT_REQUESTS_PER_MINUTE = 100

# Cache Configuration (Optional)
REDIS_URL = "redis://localhost:6379/0"

# Monitoring (Optional)
SENTRY_DSN = "your_sentry_dsn_here"

def get_database_url() -> str:
    """Get database URL from configuration."""
    # Use SQLite as fallback if PostgreSQL credentials are not properly configured
    if (POSTGRES_USER == "postgres" and POSTGRES_PASSWORD == "password") or \
       not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
        return "sqlite:///./fallback.db"
    
    return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

def is_pinecone_configured() -> bool:
    """Check if Pinecone is properly configured."""
    return (PINECONE_API_KEY and 
            PINECONE_API_KEY != "your_pinecone_api_key_here" and
            PINECONE_INDEX_NAME and 
            PINECONE_INDEX_NAME != "your_pinecone_index_name")

def is_gemini_configured() -> bool:
    """Check if Gemini is properly configured."""
    return (GEMINI_API_KEY and 
            GEMINI_API_KEY != "your_gemini_api_key_here")

def get_all_config() -> dict:
    """Get all configuration as a dictionary."""
    return {
        "database": {
            "host": POSTGRES_HOST,
            "port": POSTGRES_PORT,
            "user": POSTGRES_USER,
            "password": POSTGRES_PASSWORD,
            "database": POSTGRES_DB,
            "url": get_database_url()
        },
        "pinecone": {
            "api_key": PINECONE_API_KEY,
            "environment": PINECONE_ENVIRONMENT,
            "index_name": PINECONE_INDEX_NAME,
            "configured": is_pinecone_configured()
        },
        "gemini": {
            "api_key": GEMINI_API_KEY,
            "model": GEMINI_MODEL,
            "max_tokens": GEMINI_MAX_TOKENS,
            "temperature": GEMINI_TEMPERATURE,
            "configured": is_gemini_configured()
        },
        "embedding": {
            "model": EMBEDDING_MODEL
        },
        "app": {
            "env": APP_ENV,
            "log_level": LOG_LEVEL,
            "debug": DEBUG
        }
    }
