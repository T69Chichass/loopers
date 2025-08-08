# HackRx Document Processing System

A powerful FastAPI-based system for processing documents and answering questions using Google Gemini 2.5 Pro. This system can download documents from URLs, extract text, and provide intelligent answers to multiple questions about the document content.

## 🚀 Features

- **Document Processing**: Download and process PDF documents from URLs
- **Multiple Question Answering**: Answer multiple questions about a single document
- **Gemini 2.5 Pro Integration**: Uses Google's latest Gemini 2.5 Pro model
- **Intelligent Context Retrieval**: Finds relevant document sections for each question
- **Confidence Scoring**: Provides confidence levels for each answer
- **Supporting Evidence**: Extracts supporting text from the document
- **Robust Error Handling**: Graceful fallbacks when dependencies are unavailable
- **Fast Processing**: Optimized for quick document analysis

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API key (for full functionality)
- Internet connection (for document downloading)

## 🛠️ Installation

### 1. Clone or Download the Project

```bash
# If you have the files locally, navigate to the project directory
cd loopers
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The system is designed to work even if some heavy dependencies (like sentence-transformers) fail to install. It will use fallback implementations.

### 3. Configure API Keys

Edit `config.py` and update the Gemini API key:

```python
# Google Gemini Configuration
GEMINI_API_KEY="your_actual_gemini_api_key_here"
GEMINI_MODEL="gemini-2.5-pro"
```

**To get a Gemini API key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key and paste it in `config.py`

## 🚀 Quick Start

### 1. Start the Server

```bash
python main_hackrx.py
```

The server will start on `http://localhost:8000`

### 2. Test the Health Endpoint

```bash
curl http://localhost:8000/health
```

### 3. Use the HackRx Endpoint

The main endpoint is `POST /hackrx/run` which accepts:

```json
{
    "documents": "https://example.com/document.pdf",
    "questions": [
        "What is the grace period for premium payment?",
        "What is the waiting period for pre-existing diseases?",
        "Does this policy cover maternity expenses?"
    ]
}
```

## 📖 API Documentation

### Main Endpoint: POST /hackrx/run

**URL**: `http://localhost:8000/hackrx/run`

**Headers**:
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer your_token_here (optional)
```

**Request Body**:
```json
{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?",
        "What is the No Claim Discount (NCD) offered in this policy?",
        "Is there a benefit for preventive health check-ups?",
        "How does the policy define a 'Hospital'?",
        "What is the extent of coverage for AYUSH treatments?",
        "Are there any sub-limits on room rent and ICU charges for Plan A?"
    ]
}
```

**Response**:
```json
{
    "document_url": "https://hackrx.blob.core.windows.net/assets/policy.pdf?...",
    "questions_processed": 10,
    "answers": [
        {
            "question": "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "answer": "Based on the policy document, the grace period for premium payment is 30 days from the due date...",
            "confidence": "high",
            "supporting_evidence": [
                "The policy states that a grace period of 30 days is allowed for payment of renewal premium...",
                "During the grace period, the policy remains in force and claims are admissible..."
            ]
        }
    ],
    "processing_time": 45.23,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Health Check: GET /health

**URL**: `http://localhost:8000/health`

Returns the health status of all services.

### API Documentation: GET /docs

**URL**: `http://localhost:8000/docs`

Interactive API documentation (Swagger UI).

## 🧪 Testing

### Run the Test Script

```bash
python test_hackrx.py
```

This will test the exact request format you provided with the insurance policy document.

### Manual Testing with curl

```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer 66c272350145dbd2c98576a1ae3f62bacfcd74a73ceab1546744e495b65d67e4" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?"
    ]
}'
```

## 🔧 System Architecture

### Components

1. **SimpleDocumentProcessor** (`simple_document_processor.py`)
   - Downloads documents from URLs
   - Extracts text from PDFs using multiple libraries (PyMuPDF, PyPDF2)
   - Cleans and chunks text for processing

2. **SimpleEmbeddingManager** (`simple_embedding_manager.py`)
   - Generates embeddings for text chunks
   - Falls back to dummy embeddings if sentence-transformers is unavailable
   - Finds similar chunks using cosine similarity

3. **SimpleGeminiManager** (`simple_gemini_manager.py`)
   - Handles Gemini 2.5 Pro API calls
   - Creates optimized prompts for question answering
   - Parses responses to extract answers, confidence, and evidence

4. **Main Application** (`main_hackrx.py`)
   - FastAPI application with the `/hackrx/run` endpoint
   - Orchestrates the entire document processing pipeline
   - Handles errors and provides comprehensive responses

### Processing Pipeline

1. **Document Download**: Downloads PDF from the provided URL
2. **Text Extraction**: Extracts and cleans text from the PDF
3. **Chunking**: Splits text into manageable chunks
4. **Embedding Generation**: Creates embeddings for all chunks
5. **Question Processing**: For each question:
   - Generate embedding for the question
   - Find most similar document chunks
   - Create context-aware prompt
   - Get answer from Gemini 2.5 Pro
   - Parse and structure the response
6. **Response Assembly**: Combine all answers into final response

## 🛡️ Error Handling

The system is designed to be robust and handle various failure scenarios:

- **Missing Dependencies**: Falls back to dummy implementations
- **API Failures**: Provides informative error messages
- **Document Processing Errors**: Graceful degradation
- **Network Issues**: Timeout handling and retry logic

## 🔍 Troubleshooting

### Common Issues

1. **Server won't start**
   - Check if port 8000 is available
   - Ensure all dependencies are installed
   - Check Python version (3.8+ required)

2. **Gemini API errors**
   - Verify API key is correct in `config.py`
   - Check API quota and billing
   - Ensure internet connection

3. **Document processing fails**
   - Verify document URL is accessible
   - Check if PDF is password-protected
   - Ensure document is not corrupted

4. **Slow processing**
   - Large documents take longer to process
   - Consider reducing number of questions
   - Check system resources

### Logs

The system provides detailed logging. Check the console output for:
- Document processing status
- API call results
- Error messages
- Processing times

## 📊 Performance

Typical processing times:
- Small documents (< 10 pages): 10-30 seconds
- Medium documents (10-50 pages): 30-90 seconds
- Large documents (> 50 pages): 90+ seconds

Performance depends on:
- Document size and complexity
- Number of questions
- API response times
- System resources

## 🔒 Security

- API keys are stored in configuration files
- No sensitive data is logged
- Input validation on all endpoints
- CORS configured for development (adjust for production)

## 🚀 Production Deployment

For production deployment:

1. **Environment Variables**: Use environment variables for API keys
2. **HTTPS**: Enable HTTPS for secure communication
3. **Rate Limiting**: Implement rate limiting
4. **Monitoring**: Add application monitoring
5. **CORS**: Configure CORS for your domain
6. **Logging**: Set up proper logging infrastructure

## 📝 License

This project is provided as-is for educational and development purposes.

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Test with the provided test script
4. Verify API key configuration

---

**Happy Document Processing! 🎉**
