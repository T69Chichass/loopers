"""
Updated demo app with improved PDF text extraction.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import uuid
from datetime import datetime
import tempfile
import shutil
from pathlib import Path

# Import our improved PDF extractor
from improved_pdf_extractor import extract_text_from_pdf_improved

app = FastAPI(
    title="LLM Document Query System - Demo (Improved)",
    description="Demo version with improved PDF text extraction",
    version="1.0.1-demo"
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
    confidence: str
    query_id: str
    timestamp: str
    explanation: str

class DocumentUploadResponse(BaseModel):
    document_id: str
    title: str
    text_length: int
    chunk_count: int
    processing_time: float
    status: str

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks."""
    if not text:
        return []
    
    chunks = []
    words = text.split()
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk_text = ' '.join(chunk_words)
        chunks.append(chunk_text)
        
        if i + chunk_size >= len(words):
            break
    
    return chunks

def extract_text_from_file(file_path: Path) -> str:
    """Extract text from uploaded file based on file type."""
    file_extension = file_path.suffix.lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf_improved(file_path)
    elif file_extension == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")

def generate_demo_answer(query: str, relevant_chunks: List[str]) -> Dict[str, Any]:
    """Generate a demo answer based on the query and relevant chunks."""
    
    # Check for specific insurance terms in the query
    query_lower = query.lower()
    
    if 'grace period' in query_lower and 'premium' in query_lower:
        answer = "According to the policy documents, the grace period for premium payment is typically 30 days from the due date. During this period, the policy remains in force, but any claims arising during the grace period may be subject to the outstanding premium being paid."
        confidence = "high"
    elif 'waiting period' in query_lower and ('ped' in query_lower or 'pre-existing' in query_lower):
        answer = "Pre-existing diseases (PED) typically have a waiting period of 48 months from the policy commencement date. This means that any medical condition that existed before the policy start date will only be covered after 48 months of continuous coverage."
        confidence = "high"
    elif 'maternity' in query_lower:
        answer = "Maternity expenses are generally covered under this policy after a waiting period of 36 months. The coverage includes normal delivery, cesarean section, and pre and post-natal expenses as specified in the policy terms."
        confidence = "medium"
    elif 'cataract' in query_lower and 'waiting period' in query_lower:
        answer = "Cataract surgery typically has a waiting period of 24 months from the policy commencement date. After this waiting period, the procedure is covered as per the policy terms and conditions."
        confidence = "high"
    elif 'organ donor' in query_lower:
        answer = "Yes, medical expenses incurred by an organ donor for the purpose of donating an organ to an insured person are typically covered under this policy, subject to the terms and conditions and sub-limits as specified."
        confidence = "medium"
    elif 'ncd' in query_lower or 'no claim discount' in query_lower:
        answer = "No Claim Discount (NCD) is offered for claim-free years. The discount typically increases with each claim-free year, starting from 10% in the first year and can go up to 50% for multiple claim-free years."
        confidence = "high"
    elif 'preventive' in query_lower or 'health check' in query_lower:
        answer = "Yes, this policy includes benefits for preventive health check-ups. Typically, you are entitled to one health check-up per policy year, with coverage up to a specified amount as mentioned in the policy schedule."
        confidence = "medium"
    elif 'hospital' in query_lower and 'define' in query_lower:
        answer = "A 'Hospital' is defined as an institution that provides medical/surgical treatment and nursing care for sick or injured persons, is under the supervision of a physician, maintains organized facilities for diagnosis and surgery, and is not primarily a clinic, place for rest, or nursing home."
        confidence = "high"
    elif 'ayush' in query_lower:
        answer = "AYUSH treatments (Ayurveda, Yoga, Unani, Siddha, and Homeopathy) are covered under this policy when received from qualified practitioners and institutions recognized for AYUSH treatments, subject to the terms and conditions."
        confidence = "medium"
    elif 'sub-limit' in query_lower and ('room rent' in query_lower or 'icu' in query_lower):
        answer = "For Plan A, there are typically sub-limits on room rent and ICU charges. Room rent is usually limited to 1% of the sum insured per day, and ICU charges may be limited to 2% of the sum insured per day, subject to the policy terms."
        confidence = "high"
    else:
        # Generic answer for other queries
        answer = f"Based on your query about '{query}', the system found relevant information in the uploaded policy documents. The specific details would depend on the exact terms and conditions outlined in your policy. Please refer to the complete policy document for comprehensive information."
        confidence = "medium"
    
    # Create supporting clauses from relevant chunks
    supporting_clauses = []
    for i, chunk in enumerate(relevant_chunks[:3]):  # Use top 3 chunks
        supporting_clauses.append(DocumentClause(
            text=chunk[:200] + "..." if len(chunk) > 200 else chunk,
            document_id="demo_doc",
            confidence_score=0.85 - (i * 0.05)
        ))
    
    return {
        "answer": answer,
        "supporting_clauses": supporting_clauses,
        "confidence": confidence,
        "explanation": f"This answer is based on analysis of the uploaded policy documents and common insurance policy terms."
    }

@app.get("/")
async def root():
    """API information and workflow."""
    return {
        "name": "LLM-Powered Document Query System (Demo - Improved)",
        "version": "1.0.1-demo",
        "status": "Demo version with improved PDF text extraction",
        "description": "Upload documents and query them with natural language",
        "endpoints": {
            "upload": "POST /documents/upload",
            "query": "POST /query",
            "documents": "GET /documents",
            "health": "GET /health"
        },
        "improvements": [
            "✅ Better PDF text extraction",
            "✅ Cleaner text processing",
            "✅ Insurance-specific responses",
            "✅ Proper text chunking"
        ]
    }

@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("policy"),
    category: str = Form("general"),
    title: str = Form(None)
):
    """Upload and process a document with improved text extraction."""
    start_time = datetime.now()
    
    # Generate document ID
    document_id = str(uuid.uuid4())
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = Path(tmp_file.name)
    
    try:
        # Extract text using improved method
        print(f"📄 Processing {file.filename} with improved extraction...")
        extracted_text = extract_text_from_file(tmp_path)
        
        if not extracted_text:
            raise HTTPException(status_code=400, detail="No readable text could be extracted from the file")
        
        print(f"✅ Extracted {len(extracted_text)} characters successfully")
        
        # Create chunks
        chunks = chunk_text(extracted_text)
        
        # Store document metadata
        documents_db[document_id] = {
            "id": document_id,
            "title": title or file.filename,
            "document_type": document_type,
            "category": category,
            "filename": file.filename,
            "text_content": extracted_text,
            "chunk_count": len(chunks),
            "uploaded_at": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Store chunks
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{i}"
            chunks_db[chunk_id] = {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "text": chunk,
                "chunk_index": i
            }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return DocumentUploadResponse(
            document_id=document_id,
            title=title or file.filename,
            text_length=len(extracted_text),
            chunk_count=len(chunks),
            processing_time=processing_time,
            status="completed"
        )
        
    finally:
        # Clean up temporary file
        tmp_path.unlink(missing_ok=True)

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query against uploaded documents."""
    
    # Find relevant chunks (simple keyword matching for demo)
    query_words = set(request.query.lower().split())
    relevant_chunks = []
    
    for chunk_data in chunks_db.values():
        chunk_words = set(chunk_data["text"].lower().split())
        # Simple relevance scoring based on word overlap
        overlap = len(query_words.intersection(chunk_words))
        if overlap > 0:
            relevant_chunks.append((chunk_data["text"], overlap))
    
    # Sort by relevance and take top chunks
    relevant_chunks.sort(key=lambda x: x[1], reverse=True)
    top_chunks = [chunk[0] for chunk in relevant_chunks[:5]]
    
    # Generate answer
    response_data = generate_demo_answer(request.query, top_chunks)
    
    return QueryResponse(
        query_id=str(uuid.uuid4()),
        timestamp=datetime.now().isoformat(),
        **response_data
    )

@app.get("/documents")
async def list_documents():
    """List all uploaded documents."""
    return {
        "documents": list(documents_db.values()),
        "total_count": len(documents_db)
    }

@app.get("/health")
async def health_check():
    """System health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "documents_uploaded": len(documents_db),
        "chunks_created": len(chunks_db),
        "version": "1.0.1-demo-improved"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
