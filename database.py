"""
Database models and utilities for the FastAPI application.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class QueryLog(Base):
    """Model for logging query requests and responses."""
    
    __tablename__ = "query_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(String(50), unique=True, nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    user_id = Column(String(100), nullable=True, index=True)
    
    # Timing information
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_time = Column(Float, nullable=True)  # Total processing time in seconds
    embedding_time = Column(Float, nullable=True)   # Embedding generation time
    search_time = Column(Float, nullable=True)      # Vector search time
    llm_time = Column(Float, nullable=True)         # LLM processing time
    
    # Result information
    success = Column(Boolean, nullable=False, default=False)
    results_count = Column(Integer, nullable=True)  # Number of search results
    confidence_level = Column(String(10), nullable=True)  # high/medium/low
    
    # Response data
    answer = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<QueryLog(id={self.id}, query_id={self.query_id}, success={self.success})>"


class DocumentMetadata(Base):
    """Model for storing document metadata."""
    
    __tablename__ = "document_metadata"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Document information
    title = Column(String(500), nullable=True)
    document_type = Column(String(50), nullable=True, index=True)  # insurance, legal, hr, etc.
    category = Column(String(100), nullable=True, index=True)
    subcategory = Column(String(100), nullable=True)
    
    # File information
    filename = Column(String(255), nullable=True)
    file_path = Column(String(1000), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Processing information
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    chunk_count = Column(Integer, nullable=True)  # Number of text chunks created
    
    # Status
    processing_status = Column(String(20), default="pending", nullable=False)  # pending, processing, completed, failed
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<DocumentMetadata(id={self.id}, document_id={self.document_id}, title={self.title})>"


class DocumentChunk(Base):
    """Model for storing document chunks and their metadata."""
    
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(String(100), unique=True, nullable=False, index=True)
    document_id = Column(String(100), nullable=False, index=True)
    
    # Chunk information
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order within document
    chunk_size = Column(Integer, nullable=False)   # Character count
    
    # Context information
    page_number = Column(Integer, nullable=True)
    section_title = Column(String(500), nullable=True)
    section_type = Column(String(50), nullable=True)  # paragraph, table, list, header, etc.
    
    # Processing information
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    embedding_generated = Column(Boolean, default=False, nullable=False)
    pinecone_id = Column(String(100), nullable=True, unique=True)  # ID in Pinecone
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, chunk_id={self.chunk_id}, document_id={self.document_id})>"


# Database utility functions
def create_tables(engine):
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


def drop_tables(engine):
    """Drop all tables from the database."""
    Base.metadata.drop_all(bind=engine)
