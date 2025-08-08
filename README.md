# HackRx Document Processing System

A production-ready FastAPI application for processing documents and answering questions using Google Gemini 2.5 Pro. This system can download documents from URLs, extract text, and provide intelligent answers to multiple questions about the document content.

## 🚀 API Endpoint

**Main Endpoint**: `POST /api/v1/hackrx/run`

**Health Check**: `GET /health`

**Documentation**: `GET /docs`

## 📋 Features

- **Document Processing**: Download and process PDF documents from URLs
- **Multiple Question Answering**: Answer multiple questions about a single document
- **Gemini 2.5 Pro Integration**: Uses Google's latest Gemini 2.5 Pro model
- **Intelligent Context Retrieval**: Finds relevant document sections for each question
- **Confidence Scoring**: Provides confidence levels for each answer
- **Supporting Evidence**: Extracts supporting text from the document
- **Robust Error Handling**: Graceful fallbacks when dependencies are unavailable

## 🛠️ Deployment on Render

### 1. Prerequisites

- Render account
- Google Gemini API key

### 2. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key for deployment

### 3. Deploy on Render

1. **Fork/Clone this repository** to your GitHub account

2. **Create a new Web Service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Choose the repository with this code

3. **Configure the service**:
   - **Name**: `hackrx-document-processor` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Choose appropriate plan (Free tier works for testing)

4. **Set Environment Variables**:
   - Go to "Environment" tab
   - Add environment variable:
     - **Key**: `GEMINI_API_KEY`
     - **Value**: Your actual Gemini API key from step 2

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment to complete

### 4. Test Your Deployment

Once deployed, your API will be available at:
`https://your-app-name.onrender.com`

**Test the health endpoint**:
```bash
curl https://your-app-name.onrender.com/health
```

**Test the main endpoint**:
```bash
curl -X POST "https://your-app-name.onrender.com/api/v1/hackrx/run" \
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

## 📖 API Documentation

### Request Format

**URL**: `POST /api/v1/hackrx/run`

**Headers**:
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer your_token_here (optional)
```

**Request Body**:
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

### Response Format

```json
{
    "document_url": "https://example.com/document.pdf",
    "questions_processed": 3,
    "answers": [
        {
            "question": "What is the grace period for premium payment?",
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

## 🔧 Local Development

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variable

```bash
# Windows
set GEMINI_API_KEY=your_actual_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Run the Application

```bash
python main.py
```

The server will start on `http://localhost:8000`

## 🛡️ Error Handling

The system is designed to be robust and handle various failure scenarios:

- **Missing Dependencies**: Falls back to dummy implementations
- **API Failures**: Provides informative error messages
- **Document Processing Errors**: Graceful degradation
- **Network Issues**: Timeout handling and retry logic

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

- API keys are stored as environment variables
- No sensitive data is logged
- Input validation on all endpoints
- CORS configured for production use

## 📝 Files Structure

```
├── main.py                          # Main FastAPI application
├── models.py                        # Pydantic models for API
├── simple_document_processor.py     # Document processing logic
├── simple_embedding_manager.py      # Embedding generation
├── simple_gemini_manager.py         # Gemini API integration
├── config.py                        # Configuration settings
├── requirements.txt                 # Python dependencies
├── Procfile                         # Render deployment config
└── README.md                        # This file
```

## 🤝 Support

For issues and questions:
1. Check the Render logs for error messages
2. Verify your Gemini API key is correctly set
3. Test with the health endpoint first
4. Ensure your document URL is accessible

---

**Happy Document Processing! 🎉**
