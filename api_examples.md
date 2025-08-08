# API Usage Examples

## 🚀 LLM-Powered Document Query System API

**Base URL**: `http://localhost:8000`

---

## 📤 1. Upload Document

### cURL Example:
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_document.txt" \
  -F "document_type=insurance" \
  -F "category=auto_insurance" \
  -F "title=My Insurance Policy"
```

### Python Example:
```python
import requests

files = {
    'file': ('policy.txt', open('test_document.txt', 'rb'), 'text/plain')
}

data = {
    'document_type': 'insurance',
    'category': 'auto_insurance',
    'title': 'My Insurance Policy'
}

response = requests.post(
    'http://localhost:8000/documents/upload',
    files=files,
    data=data
)

result = response.json()
print(f"Document ID: {result['document_id']}")
```

### Response:
```json
{
  "document_id": "666896a3-1477-4c37-b728-93058c87961c",
  "title": "My Insurance Policy",
  "text_length": 1465,
  "chunk_count": 1,
  "processing_time": 0.025,
  "status": "completed"
}
```

---

## 🔍 2. Query Documents

### cURL Example:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the monthly premium?"
  }'
```

### Python Example:
```python
import requests

query_data = {
    "query": "What is the monthly premium?"
}

response = requests.post(
    'http://localhost:8000/query',
    json=query_data
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")
```

### Response:
```json
{
  "answer": "Based on your query about 'What is the monthly premium?', the system found relevant information in the uploaded policy documents...",
  "supporting_clauses": [
    {
      "text": "PREMIUM PAYMENT - Monthly premium: $150...",
      "document_id": "666896a3-1477-4c37-b728-93058c87961c",
      "confidence_score": 0.85
    }
  ],
  "confidence": "medium",
  "query_id": "abc123-def456",
  "timestamp": "2024-01-15T10:30:00Z",
  "explanation": "This answer is based on analysis of the uploaded policy documents..."
}
```

---

## 📋 3. List Documents

### cURL Example:
```bash
curl -X GET "http://localhost:8000/documents"
```

### Python Example:
```python
import requests

response = requests.get('http://localhost:8000/documents')
documents = response.json()

for doc in documents['documents']:
    print(f"ID: {doc['id']}")
    print(f"Title: {doc['title']}")
    print(f"Type: {doc['document_type']}")
    print(f"Status: {doc['status']}")
    print("---")
```

### Response:
```json
{
  "documents": [
    {
      "id": "666896a3-1477-4c37-b728-93058c87961c",
      "title": "My Insurance Policy",
      "document_type": "insurance",
      "category": "auto_insurance",
      "filename": "policy.txt",
      "text_content": "...",
      "chunk_count": 1,
      "uploaded_at": "2024-01-15T10:30:00Z",
      "status": "completed"
    }
  ],
  "total_count": 1
}
```

---

## 🏥 4. Health Check

### cURL Example:
```bash
curl -X GET "http://localhost:8000/health"
```

### Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "documents_uploaded": 1,
  "chunks_created": 1,
  "version": "1.0.0"
}
```

---

## 🗑️ 5. Delete Document

### cURL Example:
```bash
curl -X DELETE "http://localhost:8000/documents/666896a3-1477-4c37-b728-93058c87961c"
```

### Python Example:
```python
import requests

document_id = "666896a3-1477-4c37-b728-93058c87961c"
response = requests.delete(f'http://localhost:8000/documents/{document_id}')

if response.status_code == 200:
    print("Document deleted successfully")
```

---

## 📊 6. Get Document Status

### cURL Example:
```bash
curl -X GET "http://localhost:8000/documents/666896a3-1477-4c37-b728-93058c87961c"
```

### Response:
```json
{
  "document_id": "666896a3-1477-4c37-b728-93058c87961c",
  "title": "My Insurance Policy",
  "status": "completed",
  "chunk_count": 1,
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

---

## 🔄 7. Reprocess Document

### cURL Example:
```bash
curl -X POST "http://localhost:8000/documents/666896a3-1477-4c37-b728-93058c87961c/reprocess"
```

---

## 📚 API Documentation

- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## 🧪 Testing Examples

### Test with Sample Document:
```bash
# Upload the test document
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@test_document.txt" \
  -F "document_type=insurance" \
  -F "category=test" \
  -F "title=Test Policy"

# Query the document
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the monthly premium?"}'
```

### Supported File Types:
- **PDF** (.pdf)
- **Text** (.txt)
- **Word** (.docx)

### Query Examples:
- "What is the monthly premium?"
- "What are the coverage limits?"
- "How do I file a claim?"
- "What is the deductible?"
- "What is the grace period?"
