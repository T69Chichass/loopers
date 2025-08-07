"""
FastAPI application for LLM-Powered Intelligent Query-Retrieval System.
Processes natural language queries against document corpus using vector search and GPT-4.
"""
import json
import uuid
import logging
import shutil
import tempfile
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from models import (
    QueryRequest, 
    QueryResponse, 
    ErrorResponse, 
    HealthCheckResponse,
    DocumentClause,
    PineconeSearchResult,
    DocumentUploadResponse,
    DocumentStatusResponse,
    DocumentListResponse,
    DocumentDeleteResponse
)
from dependencies import (
    get_pinecone_manager,
    get_openai_manager,
    get_embedding_manager,
    get_db_session,
    check_service_health,
    PineconeManager,
    OpenAIManager,
    EmbeddingManager
)
from document_processor import DocumentProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LLM-Powered Intelligent Query-Retrieval System",
    description="API for processing natural language queries against document corpus",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting LLM Query-Retrieval System...")
    
    try:
        # Initialize all managers to ensure they're ready
        get_embedding_manager()
        get_pinecone_manager()
        get_openai_manager()
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise e


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down LLM Query-Retrieval System...")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="internal_server_error",
            message="An unexpected error occurred",
            details={"exception": str(exc)}
        ).dict()
    )


def construct_llm_prompt(query: str, context_chunks: List[PineconeSearchResult]) -> str:
    """
    Construct a comprehensive prompt for GPT-4.
    
    Args:
        query: The user's natural language question
        context_chunks: List of relevant document chunks from Pinecone
    
    Returns:
        Formatted prompt string for GPT-4
    """
    # Create context section
    context_section = "[CONTEXT]\n"
    for i, chunk in enumerate(context_chunks, 1):
        context_section += f"Document {i} (ID: {chunk.id}):\n"
        context_section += f"{chunk.text}\n"
        context_section += f"Relevance Score: {chunk.score:.3f}\n\n"
    
    # Construct the full prompt
    prompt = f"""You are an AI assistant designed to analyze legal documents, insurance policies, and corporate policies with high accuracy and attention to detail.

CORE TASK:
Analyze the provided document excerpts to answer the following user query with precision and clarity.

USER QUERY:
{query}

{context_section}

INSTRUCTIONS:
1. Do NOT use any external knowledge beyond what is provided in the context above
2. If the answer cannot be found in the provided context, state this clearly
3. Base your answer ONLY on the document excerpts provided
4. Identify specific clauses, sections, or excerpts that support your answer
5. Provide clear reasoning for your conclusions
6. Assess your confidence level in the answer (high/medium/low)

RESPONSE FORMAT:
Provide your response as a single JSON object with the following structure:
{{
    "answer": "Your clear and concise answer to the user's question",
    "supporting_clauses": [
        {{
            "text": "Exact text from the document that supports your answer",
            "document_id": "The document ID from the context",
            "confidence_score": 0.85
        }}
    ],
    "explanation": "Detailed explanation of your reasoning and how you arrived at this answer",
    "confidence": "high/medium/low - your overall confidence in this answer"
}}

IMPORTANT: Respond ONLY with the JSON object. Do not include any other text, markdown formatting, or explanations outside the JSON structure."""

    return prompt


def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Parse the JSON response from GPT-4.
    
    Args:
        response_text: Raw response text from GPT-4
    
    Returns:
        Parsed dictionary from JSON response
    
    Raises:
        ValueError: If JSON parsing fails
    """
    try:
        # Clean the response text
        cleaned_response = response_text.strip()
        
        # Find JSON object boundaries
        start_idx = cleaned_response.find('{')
        end_idx = cleaned_response.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON object found in response")
        
        json_str = cleaned_response[start_idx:end_idx]
        parsed_response = json.loads(json_str)
        
        # Validate required fields
        required_fields = ["answer", "supporting_clauses", "explanation", "confidence"]
        for field in required_fields:
            if field not in parsed_response:
                raise ValueError(f"Missing required field: {field}")
        
        return parsed_response
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        logger.error(f"Response text: {response_text}")
        raise ValueError(f"Failed to parse JSON response: {e}")
    except Exception as e:
        logger.error(f"Error parsing LLM response: {e}")
        raise ValueError(f"Error processing LLM response: {e}")


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    try:
        services = await check_service_health()
        overall_status = "healthy" if all(
            status == "healthy" for status in services.values()
        ) else "degraded"
        
        return HealthCheckResponse(
            status=overall_status,
            services=services
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse(
                error="health_check_failed",
                message="Failed to perform health check",
                details={"exception": str(e)}
            ).dict()
        )


@app.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    pinecone_manager: PineconeManager = Depends(get_pinecone_manager),
    openai_manager: OpenAIManager = Depends(get_openai_manager),
    embedding_manager: EmbeddingManager = Depends(get_embedding_manager),
    db_session=Depends(get_db_session)
):
    """
    Process a natural language query against the document corpus.
    
    Args:
        request: QueryRequest containing the user's question
        pinecone_manager: Pinecone service manager
        openai_manager: OpenAI service manager
        embedding_manager: Sentence transformer manager
        db_session: Database session for potential metadata queries
    
    Returns:
        QueryResponse with answer, supporting clauses, and explanation
    """
    query_id = str(uuid.uuid4())
    logger.info(f"Processing query {query_id}: {request.query}")
    
    try:
        # Step 1: Generate embedding for the query
        logger.info(f"Generating embedding for query {query_id}")
        query_embedding = embedding_manager.encode(request.query)
        
        # Step 2: Search for similar documents in Pinecone
        logger.info(f"Searching Pinecone for similar documents for query {query_id}")
        search_results = await pinecone_manager.search_similar(
            embedding=query_embedding,
            top_k=5
        )
        
        if not search_results:
            logger.warning(f"No search results found for query {query_id}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(
                    error="no_results_found",
                    message="No relevant documents found for the query",
                    details={"query_id": query_id}
                ).dict()
            )
        
        # Step 3: Convert Pinecone results to internal format
        context_chunks = []
        for result in search_results:
            # Extract text from metadata (assuming it's stored there)
            text_content = result.metadata.get('text', '')
            if text_content:
                context_chunks.append(PineconeSearchResult(
                    id=result.id,
                    score=result.score,
                    metadata=result.metadata,
                    text=text_content
                ))
        
        if not context_chunks:
            logger.warning(f"No text content found in search results for query {query_id}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(
                    error="no_content_found",
                    message="Search results contain no readable content",
                    details={"query_id": query_id}
                ).dict()
            )
        
        # Step 4: Construct prompt for GPT-4
        logger.info(f"Constructing LLM prompt for query {query_id}")
        llm_prompt = construct_llm_prompt(request.query, context_chunks)
        
        # Step 5: Generate response using GPT-4
        logger.info(f"Generating LLM response for query {query_id}")
        llm_response = await openai_manager.generate_response(llm_prompt)
        
        # Step 6: Parse the JSON response
        logger.info(f"Parsing LLM response for query {query_id}")
        parsed_response = parse_llm_response(llm_response)
        
        # Step 7: Convert to response model
        supporting_clauses = []
        for clause_data in parsed_response.get("supporting_clauses", []):
            supporting_clauses.append(DocumentClause(
                text=clause_data.get("text", ""),
                document_id=clause_data.get("document_id", ""),
                confidence_score=clause_data.get("confidence_score", 0.0)
            ))
        
        response = QueryResponse(
            answer=parsed_response.get("answer", ""),
            supporting_clauses=supporting_clauses,
            explanation=parsed_response.get("explanation", ""),
            confidence=parsed_response.get("confidence", "medium"),
            query_id=query_id
        )
        
        logger.info(f"Successfully processed query {query_id}")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error for query {query_id}: {e}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error="validation_error",
                message=str(e),
                details={"query_id": query_id}
            ).dict()
        )
    
    except Exception as e:
        logger.error(f"Error processing query {query_id}: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="processing_error",
                message="Failed to process query",
                details={"query_id": query_id, "exception": str(e)}
            ).dict()
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "LLM-Powered Intelligent Query-Retrieval System",
        "version": "1.0.0",
        "description": "API for processing natural language queries against document corpus",
        "workflow": [
            "1. Upload documents via POST /documents/upload",
            "2. System processes and indexes documents automatically", 
            "3. Query documents via POST /query",
            "4. Get AI-powered answers with evidence"
        ],
        "endpoints": {
            "upload_document": "POST /documents/upload",
            "list_documents": "GET /documents",
            "get_document": "GET /documents/{document_id}",
            "delete_document": "DELETE /documents/{document_id}",
            "reprocess_document": "POST /documents/{document_id}/reprocess",
            "query": "POST /query",
            "health": "GET /health",
            "docs": "GET /docs"
        },
        "supported_formats": ["PDF", "DOCX", "DOC", "TXT", "CSV"],
        "document_types": ["insurance", "legal", "hr", "policy", "contract", "manual"]
    }


@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("policy", description="Document type (insurance, legal, hr, etc.)"),
    category: str = Form("general", description="Document category"),
    title: str = Form(None, description="Document title (optional)")
):
    """
    Upload and process a document (PDF, DOCX, TXT, CSV).
    
    The document will be:
    1. Validated and stored temporarily
    2. Text extracted from the file
    3. Split into semantic chunks
    4. Embedded using sentence transformers
    5. Stored in Pinecone vector database
    6. Metadata saved to PostgreSQL
    """
    logger.info(f"Processing document upload: {file.filename}")
    
    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    file_extension = Path(file.filename).suffix.lower()
    supported_extensions = {'.pdf', '.docx', '.doc', '.txt', '.csv'}
    
    if file_extension not in supported_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_extension}. Supported: {', '.join(supported_extensions)}"
        )
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_path = temp_file.name
        shutil.copyfileobj(file.file, temp_file)
    
    try:
        # Process document
        processor = DocumentProcessor()
        metadata = {"title": title} if title else None
        
        result = await processor.process_document(
            file_path=temp_path,
            document_type=document_type,
            category=category,
            metadata=metadata
        )
        
        logger.info(f"Document processing completed: {result['document_id']}")
        
        return DocumentUploadResponse(**result)
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )
    finally:
        # Clean up temporary file
        try:
            Path(temp_path).unlink()
        except Exception as e:
            logger.warning(f"Failed to delete temporary file {temp_path}: {e}")


@app.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    document_type: str = Query(None, description="Filter by document type"),
    category: str = Query(None, description="Filter by category"),
    status: str = Query(None, description="Filter by processing status")
):
    """Get list of uploaded documents with optional filtering."""
    try:
        from sqlalchemy import and_
        from database import DocumentMetadata
        from dependencies import get_database_manager
        
        db_manager = get_database_manager()
        db = db_manager.get_db()
        
        # Build query with filters
        query = db.query(DocumentMetadata)
        filters = []
        
        if document_type:
            filters.append(DocumentMetadata.document_type == document_type)
        if category:
            filters.append(DocumentMetadata.category == category)
        if status:
            filters.append(DocumentMetadata.processing_status == status)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        documents = query.offset(offset).limit(page_size).all()
        
        # Convert to response models
        document_responses = []
        for doc in documents:
            document_responses.append(DocumentStatusResponse(
                document_id=doc.document_id,
                title=doc.title or doc.filename,
                document_type=doc.document_type,
                category=doc.category,
                filename=doc.filename,
                file_size=doc.file_size,
                processing_status=doc.processing_status,
                chunk_count=doc.chunk_count or 0,
                created_at=doc.created_at.isoformat(),
                processed_at=doc.processed_at.isoformat() if doc.processed_at else None
            ))
        
        db_manager.close_db(db)
        
        return DocumentListResponse(
            documents=document_responses,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(e)}"
        )


@app.get("/documents/{document_id}", response_model=DocumentStatusResponse)
async def get_document_status(document_id: str):
    """Get detailed status and metadata for a specific document."""
    try:
        processor = DocumentProcessor()
        result = await processor.get_document_status(document_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}"
            )
        
        return DocumentStatusResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document status: {str(e)}"
        )


@app.delete("/documents/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: str):
    """Delete a document and all its associated chunks from the system."""
    try:
        processor = DocumentProcessor()
        result = await processor.delete_document(document_id)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        logger.info(f"Document deleted: {document_id}")
        return DocumentDeleteResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@app.post("/documents/{document_id}/reprocess")
async def reprocess_document(document_id: str):
    """Reprocess an existing document (regenerate chunks and embeddings)."""
    try:
        from database import DocumentMetadata
        from dependencies import get_database_manager
        
        db_manager = get_database_manager()
        db = db_manager.get_db()
        
        # Get document metadata
        doc = db.query(DocumentMetadata).filter(
            DocumentMetadata.document_id == document_id
        ).first()
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}"
            )
        
        if not doc.file_path or not Path(doc.file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Original file not found, cannot reprocess"
            )
        
        db_manager.close_db(db)
        
        # Delete existing data
        processor = DocumentProcessor()
        await processor.delete_document(document_id)
        
        # Reprocess document
        result = await processor.process_document(
            file_path=doc.file_path,
            document_type=doc.document_type,
            category=doc.category,
            metadata={"title": doc.title}
        )
        
        logger.info(f"Document reprocessed: {document_id}")
        return DocumentUploadResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reprocess document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reprocess document: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
