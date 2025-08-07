"""
Demo version of the LLM Document Query System.
This is a simplified version to demonstrate the workflow without external dependencies.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import uuid
from datetime import datetime

app = FastAPI(
    title="LLM Document Query System - Demo",
    description="Demo version showing the document processing workflow",
    version="1.0.0-demo"
)

# In-memory storage for demo
documents_db = {}
chunks_db = {}

class QueryRequest(BaseModel):
    query: str

class DocumentClause(BaseModel):
    text: str
    document_id: str
    confidence_score: float

class QueryResponse(BaseModel):
    answer: str
    supporting_clauses: List[DocumentClause]
    explanation: str
    confidence: str
    query_id: str
    timestamp: str

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    document_type: str
    category: str
    text_length: int
    chunk_count: int
    processing_time: float
    status: str
    created_at: str

@app.get("/")
async def root():
    """API information and workflow."""
    return {
        "name": "LLM-Powered Document Query System (Demo)",
        "version": "1.0.0-demo",
        "description": "Demo showing document upload and query workflow",
        "status": "This is a demo version without AI processing",
        "workflow": [
            "1. Upload documents via POST /documents/upload",
            "2. System simulates processing and indexing",
            "3. Query documents via POST /query",
            "4. Get simulated AI-powered responses"
        ],
        "endpoints": {
            "upload_document": "POST /documents/upload",
            "list_documents": "GET /documents",
            "query": "POST /query",
            "docs": "GET /docs"
        },
        "supported_formats": ["PDF", "DOCX", "TXT"],
        "note": "This demo simulates the workflow - for full AI functionality, configure the complete system"
    }

@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("policy"),
    category: str = Form("general"),
    title: str = Form(None)
):
    """Demo document upload - simulates processing."""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Simulate reading file content
    content = await file.read()
    text_content = content.decode('utf-8', errors='ignore') if content else "Sample document content"
    
    # Create document record
    document_id = str(uuid.uuid4())
    doc_data = {
        "document_id": document_id,
        "filename": file.filename,
        "title": title or file.filename,
        "document_type": document_type,
        "category": category,
        "text_content": text_content,
        "created_at": datetime.utcnow().isoformat(),
        "status": "completed"
    }
    
    documents_db[document_id] = doc_data
    
    # Simulate chunking
    words = text_content.split()
    chunk_size = 50
    chunks = []
    
    for i in range(0, len(words), chunk_size):
        chunk_text = " ".join(words[i:i+chunk_size])
        chunk_id = f"{document_id}_chunk_{len(chunks)}"
        chunks.append({
            "chunk_id": chunk_id,
            "document_id": document_id,
            "text": chunk_text
        })
        chunks_db[chunk_id] = chunks[-1]
    
    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        document_type=document_type,
        category=category,
        text_length=len(text_content),
        chunk_count=len(chunks),
        processing_time=0.5,  # Simulated
        status="completed",
        created_at=datetime.utcnow().isoformat()
    )

@app.get("/documents")
async def list_documents():
    """List all uploaded documents."""
    documents = []
    for doc_id, doc_data in documents_db.items():
        chunk_count = sum(1 for chunk in chunks_db.values() 
                         if chunk["document_id"] == doc_id)
        documents.append({
            "document_id": doc_id,
            "title": doc_data["title"],
            "filename": doc_data["filename"],
            "document_type": doc_data["document_type"],
            "category": doc_data["category"],
            "chunk_count": chunk_count,
            "created_at": doc_data["created_at"],
            "status": doc_data["status"]
        })
    
    return {
        "documents": documents,
        "total_count": len(documents)
    }

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Demo query processing - simulates AI responses."""
    
    if not documents_db:
        raise HTTPException(
            status_code=404, 
            detail="No documents uploaded. Please upload documents first."
        )
    
    query = request.query.lower()
    query_id = str(uuid.uuid4())
    
    # Simulate finding relevant chunks (simple keyword matching)
    relevant_chunks = []
    for chunk in chunks_db.values():
        if any(word in chunk["text"].lower() for word in query.split()[:3]):
            doc_data = documents_db[chunk["document_id"]]
            relevant_chunks.append(DocumentClause(
                text=chunk["text"][:200] + "...",
                document_id=chunk["document_id"],
                confidence_score=0.85  # Simulated
            ))
            if len(relevant_chunks) >= 3:  # Limit results
                break
    
    # Generate simulated responses based on query type
    if "cover" in query or "coverage" in query:
        answer = "Based on the uploaded policy documents, coverage details depend on the specific policy terms and conditions outlined in your documents."
        explanation = "The system found relevant policy sections that discuss coverage criteria, limitations, and requirements."
        confidence = "medium"
    elif "claim" in query or "process" in query:
        answer = "To file a claim, you typically need to follow the procedures outlined in your policy documents, including proper documentation and timely submission."
        explanation = "The system identified sections related to claims processing and requirements from your uploaded documents."
        confidence = "high"
    elif "vacation" in query or "leave" in query:
        answer = "Vacation and leave policies vary by organization. Please refer to your specific employee handbook for detailed information."
        explanation = "The system found relevant sections in HR policy documents related to time off and leave policies."
        confidence = "high"
    else:
        answer = f"Based on your query about '{request.query}', the system found relevant information in the uploaded documents. The specific details depend on the content of your policy documents."
        explanation = "The system performed a semantic search across your document corpus and found potentially relevant sections."
        confidence = "medium"
    
    # If no relevant chunks found, provide a helpful message
    if not relevant_chunks:
        relevant_chunks = [DocumentClause(
            text="No specific text chunks were found for this query. This is a demo system - the full version would provide more accurate results.",
            document_id="demo",
            confidence_score=0.1
        )]
    
    return QueryResponse(
        answer=answer,
        supporting_clauses=relevant_chunks,
        explanation=explanation,
        confidence=confidence,
        query_id=query_id,
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mode": "demo",
        "documents_uploaded": len(documents_db),
        "chunks_created": len(chunks_db),
        "note": "This is a demo version - external services are simulated"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
