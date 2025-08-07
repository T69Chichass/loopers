# LLM-Powered Intelligent Query-Retrieval System

A FastAPI-based backend system that processes natural language queries against a corpus of documents (insurance, legal, HR policies) using vector search and GPT-4 to provide accurate and explainable answers.

## Features

- **Natural Language Processing**: Accept and process user queries in plain English
- **Semantic Search**: Use Pinecone vector database for intelligent document retrieval
- **LLM Integration**: Leverage GPT-4 for contextual answer generation
- **Explainable AI**: Provide supporting evidence and reasoning for answers
- **Scalable Architecture**: Built with FastAPI for high performance
- **Comprehensive Logging**: Track query processing and system health
- **Database Integration**: PostgreSQL for metadata and audit trails

## System Architecture

```
User Query → FastAPI → Embedding Generation → Pinecone Search → GPT-4 Processing → Structured Response
              ↓
         PostgreSQL (Metadata & Logs)
```

## Prerequisites

- Python 3.11+
- PostgreSQL database
- Pinecone account and index
- OpenAI API key
- Docker (optional)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd llm-query-retrieval-system
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your actual configuration:

```env
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=query_retrieval_db

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=your_pinecone_index_name

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=1500
OPENAI_TEMPERATURE=0.1
```

### 5. Database Setup

Create the PostgreSQL database and tables:

```bash
# Connect to PostgreSQL and create database
createdb query_retrieval_db

# Tables will be created automatically on first run
```

### 6. Prepare Pinecone Index

Ensure your Pinecone index is created and populated with document embeddings. The index should:
- Use dimension 384 (for all-MiniLM-L6-v2 model)
- Include metadata with text content
- Have document chunks properly indexed

## Running the Application

### Development Mode

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

Build and run with Docker:

```bash
# Build image
docker build -t llm-query-system .

# Run container
docker run -p 8000:8000 --env-file .env llm-query-system
```

## API Usage

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "services": {
    "database": "healthy",
    "pinecone": "healthy",
    "openai": "healthy",
    "embedding_model": "healthy"
  }
}
```

### Query Processing

```bash
POST /query
Content-Type: application/json

{
  "query": "Does this policy cover knee surgery, and what are the conditions?"
}
```

Response:
```json
{
  "answer": "Yes, the policy covers knee surgery under specific conditions...",
  "supporting_clauses": [
    {
      "text": "Orthopedic procedures including knee surgery are covered when medically necessary...",
      "document_id": "policy_doc_123",
      "confidence_score": 0.92
    }
  ],
  "explanation": "Based on the policy documents, knee surgery is covered when it meets the medical necessity criteria...",
  "confidence": "high",
  "query_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Project Structure

```
├── main.py                 # FastAPI application entry point
├── models.py              # Pydantic models for requests/responses
├── dependencies.py        # Dependency injection and service managers
├── database.py           # SQLAlchemy models and database utilities
├── config.py             # Configuration management
├── logging_config.py     # Logging setup and utilities
├── exceptions.py         # Custom exception classes
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
├── env.example         # Environment variables template
└── README.md          # This file
```

## Core Components

### 1. Query Processing Pipeline

1. **Input Validation**: Validate user query using Pydantic models
2. **Embedding Generation**: Generate vector embedding using sentence-transformers
3. **Vector Search**: Query Pinecone for relevant document chunks
4. **Context Assembly**: Compile retrieved chunks into structured context
5. **LLM Prompting**: Send formatted prompt to GPT-4
6. **Response Parsing**: Extract and validate JSON response
7. **Result Formatting**: Return structured response to user

### 2. Service Managers

- **DatabaseManager**: PostgreSQL connection and session management
- **PineconeManager**: Vector database operations
- **OpenAIManager**: GPT-4 API interactions
- **EmbeddingManager**: Sentence transformer model operations

### 3. Error Handling

Comprehensive error handling with:
- Custom exception classes
- HTTP status code mapping
- Detailed error messages
- Request ID tracking
- Structured logging

### 4. Monitoring and Logging

- Structured query logging
- Performance metrics tracking
- Service health monitoring
- Request/response audit trails

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_HOST` | PostgreSQL host | localhost |
| `POSTGRES_PORT` | PostgreSQL port | 5432 |
| `POSTGRES_USER` | Database username | Required |
| `POSTGRES_PASSWORD` | Database password | Required |
| `POSTGRES_DB` | Database name | Required |
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `PINECONE_ENVIRONMENT` | Pinecone environment | Required |
| `PINECONE_INDEX_NAME` | Pinecone index name | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model | gpt-4 |
| `OPENAI_MAX_TOKENS` | Max response tokens | 1500 |
| `OPENAI_TEMPERATURE` | Model temperature | 0.1 |
| `EMBEDDING_MODEL` | Sentence transformer model | all-MiniLM-L6-v2 |

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
flake8 .
```

### Type Checking

```bash
mypy .
```

## Production Deployment

### Security Considerations

1. Use environment-specific configurations
2. Enable HTTPS/TLS
3. Configure proper CORS settings
4. Implement rate limiting
5. Use secrets management
6. Set up monitoring and alerting

### Scaling

- Use multiple workers with uvicorn
- Deploy behind a load balancer
- Consider horizontal scaling with container orchestration
- Implement caching for frequent queries
- Monitor resource usage and performance

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify environment variables
   - Check service availability
   - Review network configuration

2. **Empty Search Results**
   - Verify Pinecone index is populated
   - Check embedding model compatibility
   - Review query complexity

3. **LLM Response Parsing**
   - Check OpenAI API status
   - Review prompt formatting
   - Verify JSON response structure

### Logs and Debugging

Check application logs for detailed error information:

```bash
# View logs in development
tail -f logs/app.log

# In Docker
docker logs <container-id>
```

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
