# LLM-Powered Document Query System

A sophisticated AI-powered system for processing and querying insurance policy documents using natural language. Built with FastAPI, OpenAI GPT-4, Pinecone vector database, and advanced document processing capabilities.

## 🚀 Features

- **📄 Multi-format Document Support**: PDF, TXT, DOCX files
- **🤖 AI-Powered Queries**: Natural language processing with GPT-4
- **🔍 Vector Search**: Semantic similarity search with Pinecone
- **📊 Intelligent Chunking**: Advanced text segmentation for optimal retrieval
- **🎯 Confidence Scoring**: Reliability indicators for answers
- **📚 Supporting Evidence**: Relevant document excerpts with each answer
- **🔄 Real-time Processing**: Fast document upload and query processing
- **🏥 Insurance-Specific**: Optimized for insurance policy analysis

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Document      │    │   FastAPI       │    │   OpenAI        │
│   Upload        │───▶│   Server        │───▶│   GPT-4         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Pinecone      │
                       │   Vector DB     │
                       └─────────────────┘
```

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL database
- Pinecone account and API key
- OpenAI API key

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd loopers
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and database credentials
   ```

4. **Configure your API keys**
   ```bash
   python configure_apis.py
   ```

## 🚀 Quick Start

### 1. Start the API Server
```bash
python main.py
```
The server will start at `http://localhost:8000`

### 2. Access API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 3. Upload and Query Documents
```bash
# Run the example script
python examples/process_insurance_policy.py
```

## 📖 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | System information |
| `/health` | GET | Health check |
| `/documents/upload` | POST | Upload document |
| `/query` | POST | Process natural language query |
| `/documents` | GET | List uploaded documents |
| `/documents/{id}` | GET | Get document status |
| `/documents/{id}` | DELETE | Delete document |

### Example Usage

#### Upload Document
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@policy.pdf" \
  -F "document_type=insurance" \
  -F "category=health_insurance" \
  -F "title=My Insurance Policy"
```

#### Query Document
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the grace period for premium payment?"}'
```

## 🧪 Testing

### Run Demo Workflow
```bash
python test_demo_workflow.py
```

### Test API Endpoints
```bash
python test_api.py
```

### Test Document Processing
```bash
python test_document_processing.py
```

## 📁 Project Structure

```
loopers/
├── src/                          # Source code
│   └── policy_processor.py       # Clean policy processor
├── examples/                     # Example scripts
│   └── process_insurance_policy.py
├── tests/                        # Test files
├── main.py                       # FastAPI application
├── demo_improved.py              # Demo version
├── requirements.txt              # Dependencies
├── config.py                     # Configuration
├── models.py                     # Data models
├── dependencies.py               # Dependency injection
├── document_processor.py         # Document processing
├── improved_pdf_extractor.py     # PDF text extraction
├── database.py                   # Database models
├── exceptions.py                 # Custom exceptions
├── logging_config.py             # Logging configuration
└── README.md                     # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=query_retrieval_db

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=your_index_name

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=1500
OPENAI_TEMPERATURE=0.1

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
DEBUG=True
```

## 🎯 Use Cases

### Insurance Policy Analysis
- **Grace Period Queries**: Premium payment deadlines
- **Waiting Period Analysis**: Pre-existing conditions coverage
- **Maternity Benefits**: Coverage conditions and limitations
- **Surgical Procedures**: Waiting periods and coverage
- **Claim Process**: Documentation and submission requirements

### Document Types Supported
- **Insurance Policies**: Health, auto, life insurance
- **Legal Documents**: Contracts, agreements
- **HR Documents**: Employee handbooks, policies
- **Medical Records**: Patient documentation
- **Financial Documents**: Reports, statements

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up --build
```

### Production Deployment
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📊 Performance

- **Document Processing**: ~6 seconds for 100KB PDF
- **Query Response**: ~3 seconds per query
- **Text Extraction**: 99%+ accuracy
- **Vector Search**: Sub-second retrieval
- **AI Response**: High-quality, contextual answers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test files for examples

## 🔄 Changelog

### v1.0.0
- Initial release
- FastAPI-based API
- OpenAI GPT-4 integration
- Pinecone vector search
- PDF/TXT/DOCX support
- Insurance policy optimization

---

**Built with ❤️ for intelligent document processing**
