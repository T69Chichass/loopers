# 📄 Complete Document Processing Workflow

This guide shows you how to use the LLM-Powered Intelligent Query-Retrieval System from uploading policy documents to querying them.

## 🚀 Complete Workflow Overview

```
1. Upload Policy Documents (PDF/DOCX/TXT) → 
2. System Processes & Indexes Documents → 
3. Query Documents with Natural Language → 
4. Get AI-Powered Answers with Evidence
```

## 📋 Prerequisites

1. **API Server Running**
   ```bash
   python main.py
   # Server running at http://localhost:8000
   ```

2. **Required Environment Variables** (in `.env`)
   ```env
   POSTGRES_HOST=localhost
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=query_retrieval_db
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_ENVIRONMENT=your_environment
   PINECONE_INDEX_NAME=your_index
   OPENAI_API_KEY=your_openai_key
   ```

## 📤 Step 1: Upload Policy Documents

### Upload via cURL
```bash
# Upload a PDF insurance policy
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@insurance_policy.pdf" \
     -F "document_type=insurance" \
     -F "category=health_insurance" \
     -F "title=Corporate Health Insurance Policy 2024"

# Upload an HR policy document
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@employee_handbook.docx" \
     -F "document_type=hr" \
     -F "category=policies" \
     -F "title=Employee Handbook"

# Upload a legal contract
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@service_agreement.pdf" \
     -F "document_type=legal" \
     -F "category=contracts"
```

### Upload via Python
```python
import requests

# Upload insurance policy
with open('insurance_policy.pdf', 'rb') as f:
    files = {'file': f}
    data = {
        'document_type': 'insurance',
        'category': 'health_insurance',
        'title': 'Corporate Health Insurance Policy 2024'
    }
    
    response = requests.post(
        'http://localhost:8000/documents/upload',
        files=files,
        data=data
    )
    
    result = response.json()
    print(f"Document uploaded: {result['document_id']}")
    print(f"Processing time: {result['processing_time']:.2f}s")
    print(f"Text chunks created: {result['chunk_count']}")
```

### Expected Upload Response
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "insurance_policy.pdf",
  "document_type": "insurance",
  "category": "health_insurance",
  "text_length": 15420,
  "chunk_count": 23,
  "embeddings_created": 23,
  "processing_time": 12.45,
  "status": "completed",
  "created_at": "2024-01-01T12:00:00Z"
}
```

## 📋 Step 2: Manage Documents

### List All Documents
```bash
# Get all documents
curl "http://localhost:8000/documents"

# Filter by document type
curl "http://localhost:8000/documents?document_type=insurance"

# Filter by category
curl "http://localhost:8000/documents?category=health_insurance"

# Paginate results
curl "http://localhost:8000/documents?page=1&page_size=5"
```

### Check Document Status
```bash
curl "http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000"
```

### Delete Document (if needed)
```bash
curl -X DELETE "http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000"
```

## 🔍 Step 3: Query Your Documents

Now that your documents are processed and indexed, you can ask questions!

### Basic Queries via cURL
```bash
# Insurance coverage query
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "Does this insurance policy cover knee surgery?"
     }'

# HR policy query
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What is the vacation policy for new employees?"
     }'

# Legal contract query
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What are the termination conditions in this contract?"
     }'
```

### Advanced Queries via Python
```python
import requests

def query_documents(question):
    response = requests.post(
        'http://localhost:8000/query',
        json={'query': question}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Question: {question}")
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Supporting Evidence:")
        
        for i, clause in enumerate(result['supporting_clauses'], 1):
            print(f"  {i}. {clause['text'][:100]}...")
            print(f"     (Document: {clause['document_id']}, Score: {clause['confidence_score']:.2f})")
        
        print(f"Explanation: {result['explanation']}")
        print("-" * 80)
    else:
        print(f"Error: {response.json()}")

# Example queries
queries = [
    "What medical procedures are covered under this policy?",
    "Are pre-existing conditions covered?",
    "What is the maximum coverage limit?",
    "How do I file a claim?",
    "What are the exclusions in this policy?",
    "Is mental health treatment covered?",
    "What is the deductible amount?",
    "Are prescription drugs covered?"
]

for query in queries:
    query_documents(query)
```

## 📊 Expected Query Response
```json
{
  "answer": "Yes, knee surgery is covered under this policy when it is medically necessary and pre-authorized by your primary care physician. The coverage includes both arthroscopic and total knee replacement procedures.",
  "supporting_clauses": [
    {
      "text": "Orthopedic procedures including knee surgery, hip surgery, and joint replacements are covered when medically necessary and pre-authorized by the member's primary care physician.",
      "document_id": "550e8400-e29b-41d4-a716-446655440000",
      "confidence_score": 0.92
    },
    {
      "text": "All surgical procedures require prior authorization except for emergency procedures. Members must obtain approval within 48 hours for emergency surgeries.",
      "document_id": "550e8400-e29b-41d4-a716-446655440000",
      "confidence_score": 0.85
    }
  ],
  "explanation": "Based on the policy documents, knee surgery is covered under the orthopedic procedures section. The policy clearly states that such procedures are covered when they meet medical necessity criteria and have been pre-authorized by your primary care physician. This includes both routine and emergency surgical procedures.",
  "confidence": "high",
  "query_id": "abc123-def456-ghi789",
  "timestamp": "2024-01-01T12:30:00Z"
}
```

## 🎯 Use Case Examples

### 1. Insurance Policy Queries
```bash
# Coverage questions
"Does this policy cover dental procedures?"
"What is the annual deductible?"
"Are mental health services included?"
"How much does an emergency room visit cost?"

# Claims and procedures
"How do I submit a claim?"
"What documents are needed for reimbursement?"
"What is the appeal process if a claim is denied?"
"Are there any network restrictions?"
```

### 2. HR Policy Queries
```bash
# Employee benefits
"What are the vacation days for new employees?"
"Is there a work-from-home policy?"
"What is the maternity leave policy?"
"Are there professional development opportunities?"

# Procedures and guidelines
"What is the disciplinary action process?"
"How do I report workplace harassment?"
"What are the performance review criteria?"
"Is there a dress code policy?"
```

### 3. Legal Contract Queries
```bash
# Contract terms
"What are the payment terms in this agreement?"
"How can this contract be terminated?"
"What are the liability limitations?"
"Are there any penalty clauses?"

# Rights and obligations
"What are my responsibilities under this contract?"
"What happens if there's a breach of contract?"
"Are there any confidentiality requirements?"
"What is the dispute resolution process?"
```

## 🔧 System Capabilities

### Supported Document Types
- **PDF**: Insurance policies, legal contracts, manuals
- **DOCX/DOC**: Employee handbooks, policy documents
- **TXT**: Plain text policies and procedures
- **CSV**: Structured data like benefit tables

### Document Processing Features
- ✅ **Text Extraction**: Smart extraction from various formats
- ✅ **Semantic Chunking**: Intelligent text segmentation
- ✅ **Vector Embeddings**: High-quality semantic representations
- ✅ **Metadata Storage**: Document organization and tracking
- ✅ **Error Handling**: Robust processing with detailed feedback

### Query Processing Features
- ✅ **Natural Language Understanding**: Ask questions in plain English
- ✅ **Semantic Search**: Find relevant content across all documents
- ✅ **Evidence-Based Answers**: Responses backed by source material
- ✅ **Confidence Scoring**: Reliability indicators for answers
- ✅ **Explainable AI**: Clear reasoning and source citations

## 📈 Performance Tips

### 1. Document Optimization
- **File Size**: Keep documents under 50MB for optimal processing
- **Quality**: Use high-quality scanned PDFs for better text extraction
- **Structure**: Well-formatted documents process more accurately

### 2. Query Optimization
- **Specificity**: Ask specific questions for better results
- **Context**: Include relevant context in your queries
- **Keywords**: Use domain-specific terms when appropriate

### 3. System Monitoring
- **Health Check**: Regularly monitor `/health` endpoint
- **Document Status**: Check processing status for large files
- **Response Times**: Monitor query performance

## 🚨 Troubleshooting

### Common Issues

1. **Document Upload Failures**
   ```bash
   # Check file format
   curl "http://localhost:8000/health"
   
   # Verify file size (< 50MB recommended)
   ls -lh your_document.pdf
   ```

2. **No Search Results**
   ```bash
   # Verify document was processed
   curl "http://localhost:8000/documents"
   
   # Check document status
   curl "http://localhost:8000/documents/{document_id}"
   ```

3. **Poor Answer Quality**
   - Try rephrasing your question
   - Use more specific terms
   - Check if relevant documents are uploaded

### Getting Help
- **API Documentation**: Visit `http://localhost:8000/docs`
- **Health Status**: Check `http://localhost:8000/health`
- **Document List**: Review `http://localhost:8000/documents`

## 🎉 Success! 

You now have a complete document processing and query system that can:

1. ✅ **Ingest** policy documents from various formats
2. ✅ **Process** and index them for semantic search
3. ✅ **Answer** natural language questions with evidence
4. ✅ **Provide** explainable AI responses with source citations

Your LLM-powered query system is ready to help users find answers in your document corpus!
