"""
Main FastAPI application with hackrx/run endpoint for document processing and question answering.
"""
import json
import logging
import time
from typing import Dict, Any, List
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from models import (
    HackRxRequest, 
    HackRxResponse, 
    HackRxQuestionResponse,
    ErrorResponse, 
    HealthCheckResponse
)
from simple_document_processor import get_document_processor
from simple_embedding_manager import get_simple_embedding_manager
from simple_gemini_manager import get_simple_gemini_manager
from config import GEMINI_API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI."""
    # Startup
    logger.info("Starting HackRx Document Processing System...")
    
    try:
        # Initialize managers
        get_document_processor()
        get_simple_embedding_manager()
        get_simple_gemini_manager(GEMINI_API_KEY)
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        # Don't raise - allow the app to start with limited functionality
    
    yield
    
    # Shutdown
    logger.info("Shutting down HackRx Document Processing System...")

# Create FastAPI app
app = FastAPI(
    title="HackRx Document Processing System",
    description="API for processing documents and answering questions using Gemini 2.5 Pro",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    error_response = ErrorResponse(
        error="internal_server_error",
        message="An unexpected error occurred",
        details={"exception": str(exc)}
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check basic services
        services = {
            "server": "healthy",
            "document_processor": "healthy",
            "embedding_manager": "healthy",
            "gemini_manager": "healthy"
        }
        
        # Test Gemini connection
        try:
            gemini_manager = get_simple_gemini_manager(GEMINI_API_KEY)
            if gemini_manager.test_connection():
                services["gemini_api"] = "healthy"
            else:
                services["gemini_api"] = "unhealthy"
        except Exception:
            services["gemini_api"] = "unhealthy"
        
        overall_status = "healthy" if all(
            status == "healthy" for status in services.values()
        ) else "degraded"
        
        return HealthCheckResponse(
            status=overall_status,
            services=services
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        error_response = ErrorResponse(
            error="health_check_failed",
            message="Failed to perform health check",
            details={"exception": str(e)}
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response.model_dump()
        )

@app.post("/hackrx/run", response_model=HackRxResponse)
async def hackrx_run(request: HackRxRequest):
    """
    Process a document from URL and answer multiple questions about it.
    
    This endpoint:
    1. Downloads the document from the provided URL
    2. Extracts text from the document
    3. Splits text into chunks for processing
    4. For each question, finds relevant chunks and generates answers using Gemini 2.5 Pro
    5. Returns comprehensive answers with confidence levels and supporting evidence
    """
    start_time = time.time()
    logger.info(f"Processing hackrx request for document: {request.documents}")
    logger.info(f"Number of questions: {len(request.questions)}")
    
    try:
        # Step 1: Process the document
        logger.info("Step 1: Processing document...")
        doc_processor = get_document_processor()
        doc_result = await doc_processor.process_document_from_url(request.documents)
        
        document_text = doc_result['text']
        document_chunks = doc_result['chunks']
        
        logger.info(f"Document processed: {len(document_text)} characters, {len(document_chunks)} chunks")
        
        if not document_chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text content could be extracted from the document"
            )
        
        # Step 2: Initialize managers
        logger.info("Step 2: Initializing managers...")
        embedding_manager = get_simple_embedding_manager()
        gemini_manager = get_simple_gemini_manager(GEMINI_API_KEY)
        
        # Step 3: Generate embeddings for document chunks
        logger.info("Step 3: Generating embeddings for document chunks...")
        chunk_embeddings = embedding_manager.encode_batch(document_chunks)
        
        # Step 4: Process each question
        logger.info("Step 4: Processing questions...")
        answers = []
        
        for i, question in enumerate(request.questions):
            logger.info(f"Processing question {i+1}/{len(request.questions)}: {question[:50]}...")
            
            try:
                # Generate embedding for the question
                question_embedding = embedding_manager.encode(question)
                
                # Find similar chunks
                similar_chunks = embedding_manager.find_similar_chunks(
                    question_embedding, 
                    chunk_embeddings, 
                    top_k=3
                )
                
                # Get the most relevant chunks
                relevant_chunks = []
                for chunk_idx, similarity_score in similar_chunks:
                    if similarity_score > 0.1:  # Minimum similarity threshold
                        relevant_chunks.append(document_chunks[chunk_idx])
                
                # If no relevant chunks found, use first few chunks
                if not relevant_chunks and document_chunks:
                    relevant_chunks = document_chunks[:2]
                
                # Generate answer using Gemini
                answer_result = await gemini_manager.answer_question_with_context(
                    question, 
                    relevant_chunks
                )
                
                # Create response object
                question_response = HackRxQuestionResponse(
                    question=question,
                    answer=answer_result["answer"],
                    confidence=answer_result["confidence"],
                    supporting_evidence=answer_result["supporting_evidence"]
                )
                
                answers.append(question_response)
                logger.info(f"Question {i+1} processed successfully")
                
            except Exception as e:
                logger.error(f"Failed to process question {i+1}: {e}")
                # Create error response for this question
                error_response = HackRxQuestionResponse(
                    question=question,
                    answer=f"I apologize, but I encountered an error while processing this question: {str(e)}",
                    confidence="low",
                    supporting_evidence=[]
                )
                answers.append(error_response)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create final response
        response = HackRxResponse(
            document_url=request.documents,
            questions_processed=len(answers),
            answers=answers,
            processing_time=processing_time
        )
        
        logger.info(f"HackRx processing completed in {processing_time:.2f} seconds")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"HackRx processing failed: {e}")
        error_response = ErrorResponse(
            error="processing_error",
            message="Failed to process document and questions",
            details={"exception": str(e)}
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump()
        )

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "HackRx Document Processing System",
        "version": "1.0.0",
        "description": "API for processing documents and answering questions using Gemini 2.5 Pro",
        "main_endpoint": "POST /hackrx/run",
        "health_check": "GET /health",
        "documentation": "GET /docs",
        "features": [
            "Document processing from URLs",
            "Multiple question answering",
            "Gemini 2.5 Pro integration",
            "Confidence scoring",
            "Supporting evidence extraction"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_hackrx:app",
        host="127.0.0.1",
        port=5000,
        reload=False,
        log_level="info"
    )
