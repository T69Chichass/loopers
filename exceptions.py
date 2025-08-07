"""
Custom exceptions for the FastAPI application.
"""
from typing import Optional, Dict, Any


class BaseQueryException(Exception):
    """Base exception for query processing errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "unknown_error",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class EmbeddingGenerationError(BaseQueryException):
    """Raised when embedding generation fails."""
    
    def __init__(self, message: str = "Failed to generate embeddings", **kwargs):
        super().__init__(message, error_code="embedding_generation_error", **kwargs)


class VectorSearchError(BaseQueryException):
    """Raised when vector search fails."""
    
    def __init__(self, message: str = "Vector search failed", **kwargs):
        super().__init__(message, error_code="vector_search_error", **kwargs)


class LLMRequestError(BaseQueryException):
    """Raised when LLM request fails."""
    
    def __init__(self, message: str = "LLM request failed", **kwargs):
        super().__init__(message, error_code="llm_request_error", **kwargs)


class LLMResponseParsingError(BaseQueryException):
    """Raised when LLM response cannot be parsed."""
    
    def __init__(self, message: str = "Failed to parse LLM response", **kwargs):
        super().__init__(message, error_code="llm_response_parsing_error", **kwargs)


class DatabaseConnectionError(BaseQueryException):
    """Raised when database connection fails."""
    
    def __init__(self, message: str = "Database connection failed", **kwargs):
        super().__init__(message, error_code="database_connection_error", **kwargs)


class PineconeConnectionError(BaseQueryException):
    """Raised when Pinecone connection fails."""
    
    def __init__(self, message: str = "Pinecone connection failed", **kwargs):
        super().__init__(message, error_code="pinecone_connection_error", **kwargs)


class OpenAIConnectionError(BaseQueryException):
    """Raised when OpenAI API connection fails."""
    
    def __init__(self, message: str = "OpenAI API connection failed", **kwargs):
        super().__init__(message, error_code="openai_connection_error", **kwargs)


class ConfigurationError(BaseQueryException):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str = "Invalid configuration", **kwargs):
        super().__init__(message, error_code="configuration_error", **kwargs)


class ValidationError(BaseQueryException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str = "Input validation failed", **kwargs):
        super().__init__(message, error_code="validation_error", **kwargs)


class NoResultsFoundError(BaseQueryException):
    """Raised when no search results are found."""
    
    def __init__(self, message: str = "No relevant documents found", **kwargs):
        super().__init__(message, error_code="no_results_found", **kwargs)


class RateLimitExceededError(BaseQueryException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, error_code="rate_limit_exceeded", **kwargs)
