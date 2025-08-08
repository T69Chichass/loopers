# LLM System 6-Step Workflow Implementation

## Overview
This document details how the LLM-Powered Intelligent Query-Retrieval System implements the 6-step workflow for processing natural language queries against document corpora.

## The 6-Step Workflow

### 1. Input Documents (PDF Blob URL)
**Implementation**: `POST /documents/upload` endpoint
- **File Support**: PDF, DOCX, DOC, TXT, CSV
- **Processing**: Text extraction, cleaning, and chunking
- **Storage**: PostgreSQL metadata + Pinecone vector embeddings

**Code Location**: `document_processor.py` - `process_document()` method
```python
# Step 1: Document Upload and Processing
extracted_text = await self._extract_text(file_path)
chunks = await self._create_chunks(extracted_text, document_id)
embeddings = await self._process_embeddings(chunks, document_id)
```

### 2. LLM Parser (Extract Structured Query)
**Implementation**: Query preprocessing and embedding generation
- **Input**: Natural language query from user
- **Processing**: Text normalization and embedding generation
- **Output**: Vector representation for similarity search

**Code Location**: `main.py` - `process_query()` method, Step 1
```python
# Step 2: Generate embedding for the query
query_embedding = embedding_manager.encode(request.query)
```

### 3. Embedding Search (FAISS/Pinecone Retrieval)
**Implementation**: Vector similarity search using Pinecone
- **Search**: Top-k similar document chunks
- **Algorithm**: Cosine similarity on sentence embeddings
- **Results**: Ranked list of relevant document chunks

**Code Location**: `main.py` - `process_query()` method, Step 2
```python
# Step 3: Search for similar documents in Pinecone
search_results = await pinecone_manager.search_similar(
    embedding=query_embedding,
    top_k=5
)
```

### 4. Clause Matching (Semantic Similarity)
**Implementation**: Context chunk processing and relevance scoring
- **Processing**: Extract text content from search results
- **Scoring**: Use relevance scores from vector search
- **Filtering**: Remove low-quality or irrelevant chunks

**Code Location**: `main.py` - `process_query()` method, Step 3
```python
# Step 4: Convert Pinecone results to internal format
context_chunks = []
for result in search_results:
    text_content = result.metadata.get('text', '')
    if text_content:
        context_chunks.append(PineconeSearchResult(
            id=result.id,
            score=result.score,
            metadata=result.metadata,
            text=text_content
        ))
```

### 5. Logic Evaluation (Decision Processing)
**Implementation**: GPT-4 prompt construction and response generation
- **Prompt Engineering**: Structured prompt with context and instructions
- **LLM Processing**: GPT-4 analyzes context and generates structured response
- **Reasoning**: AI evaluates evidence and provides explanations

**Code Location**: `main.py` - `construct_llm_prompt()` and `process_query()` method, Steps 4-5
```python
# Step 5: Construct prompt for GPT-4
llm_prompt = construct_llm_prompt(request.query, context_chunks)

# Step 6: Generate response using GPT-4
llm_response = await openai_manager.generate_response(llm_prompt)
```

### 6. JSON Output (Structured Response)
**Implementation**: Response parsing and structured output
- **Parsing**: Extract JSON from LLM response
- **Validation**: Ensure required fields are present
- **Formatting**: Return structured QueryResponse object

**Code Location**: `main.py` - `parse_llm_response()` and `process_query()` method, Step 6
```python
# Step 7: Parse the JSON response
parsed_response = parse_llm_response(llm_response)

# Step 8: Convert to response model
response = QueryResponse(
    answer=parsed_response.get("answer", ""),
    supporting_clauses=supporting_clauses,
    explanation=parsed_response.get("explanation", ""),
    confidence=parsed_response.get("confidence", "medium"),
    query_id=query_id
)
```

## Database Schema Support

### QueryLog Table
- Tracks each step's processing time
- Stores query metadata and results
- Enables performance monitoring

### DocumentMetadata Table
- Stores document information and processing status
- Tracks chunk counts and file metadata

### DocumentChunk Table
- Stores individual text chunks
- Links chunks to Pinecone embeddings
- Enables chunk-level retrieval

## API Endpoints

### Document Processing
- `POST /documents/upload` - Step 1: Input Documents
- `GET /documents` - List processed documents
- `GET /documents/{id}` - Get document status

### Query Processing
- `POST /query` - Steps 2-6: Complete workflow
- `GET /health` - System status check

## Example Workflow

1. **Upload Document**: `POST /documents/upload` with PDF file
2. **Process Query**: `POST /query` with natural language question
3. **Receive Response**: Structured JSON with answer and evidence

## Performance Metrics

The system tracks timing for each step:
- Embedding generation time
- Vector search time
- LLM processing time
- Total processing time

## Error Handling

Each step includes comprehensive error handling:
- File validation errors
- Embedding generation failures
- Search result validation
- LLM response parsing errors
- Database connection issues
