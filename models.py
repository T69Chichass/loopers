"""
Pydantic models for request and response validation.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for the query endpoint."""
    query: str = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="The user's natural language question"
    )
    
    @validator('query')
    def validate_query(cls, v):
        """Validate that the query is not empty or just whitespace."""
        if not v.strip():
            raise ValueError('Query cannot be empty or just whitespace')
        return v.strip()


class DocumentClause(BaseModel):
    """Model representing a specific document clause or excerpt."""
    text: str = Field(..., description="The text content of the clause")
    document_id: str = Field(..., description="The ID of the source document")
    confidence_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence score from vector similarity search"
    )


class QueryResponse(BaseModel):
    """Response model for the query endpoint."""
    answer: str = Field(..., description="The AI-generated answer to the query")
    supporting_clauses: List[DocumentClause] = Field(
        ..., 
        description="List of document clauses that support the answer"
    )
    explanation: str = Field(
        ..., 
        description="Explanation of the reasoning behind the answer"
    )
    confidence: str = Field(
        ..., 
        description="Overall confidence level in the answer (high/medium/low)"
    )
    query_id: Optional[str] = Field(
        None, 
        description="Unique identifier for this query (for tracking/logging)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the query was processed"
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional error details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the error occurred"
    )


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the health check"
    )
    services: Dict[str, str] = Field(
        ..., 
        description="Status of individual services (database, pinecone, openai)"
    )


class PineconeSearchResult(BaseModel):
    """Model for internal Pinecone search results."""
    id: str = Field(..., description="Pinecone vector ID")
    score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Associated metadata"
    )
    text: str = Field(..., description="Original text content")


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    document_type: str = Field(..., description="Document type")
    category: str = Field(..., description="Document category")
    text_length: int = Field(..., description="Extracted text length")
    chunk_count: int = Field(..., description="Number of text chunks created")
    embeddings_created: int = Field(..., description="Number of embeddings generated")
    processing_time: float = Field(..., description="Processing time in seconds")
    status: str = Field(..., description="Processing status")
    created_at: str = Field(..., description="Creation timestamp")


class DocumentStatusResponse(BaseModel):
    """Response model for document status."""
    document_id: str = Field(..., description="Document identifier")
    title: str = Field(..., description="Document title")
    document_type: str = Field(..., description="Document type")
    category: str = Field(..., description="Document category")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    processing_status: str = Field(..., description="Current processing status")
    chunk_count: int = Field(..., description="Number of chunks created")
    created_at: str = Field(..., description="Creation timestamp")
    processed_at: Optional[str] = Field(None, description="Processing completion timestamp")


class DocumentListResponse(BaseModel):
    """Response model for document list."""
    documents: List[DocumentStatusResponse] = Field(..., description="List of documents")
    total_count: int = Field(..., description="Total number of documents")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=10, description="Page size")


class DocumentDeleteResponse(BaseModel):
    """Response model for document deletion."""
    document_id: str = Field(..., description="Document identifier")
    status: str = Field(..., description="Deletion status")
    chunks_deleted: int = Field(..., description="Number of chunks deleted")
