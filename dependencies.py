"""
Dependency injection for FastAPI application.
Manages connections to external services and shared resources.
"""
import os
import logging
from typing import Optional, Dict, Any
from functools import lru_cache
from contextlib import asynccontextmanager

import pinecone
import openai
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database
Base = declarative_base()


class DatabaseManager:
    """Manages PostgreSQL database connections."""
    
    def __init__(self):
        self.database_url = self._get_database_url()
        self.engine = create_engine(
            self.database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def _get_database_url(self) -> str:
        """Construct database URL from environment variables."""
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DB")
        
        if not all([user, password, database]):
            raise ValueError("Missing required PostgreSQL environment variables")
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    def get_db(self) -> Session:
        """Get database session."""
        db = self.SessionLocal()
        try:
            return db
        except Exception as e:
            db.close()
            raise e
    
    def close_db(self, db: Session):
        """Close database session."""
        db.close()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            db = self.get_db()
            db.execute("SELECT 1")
            self.close_db(db)
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


class PineconeManager:
    """Manages Pinecone vector database connections."""
    
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.environment = os.getenv("PINECONE_ENVIRONMENT")
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        
        if not all([self.api_key, self.environment, self.index_name]):
            raise ValueError("Missing required Pinecone environment variables")
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Pinecone client and index."""
        try:
            pinecone.init(
                api_key=self.api_key,
                environment=self.environment
            )
            self.index = pinecone.Index(self.index_name)
            logger.info("Pinecone client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise e
    
    async def search_similar(
        self, 
        embedding: list, 
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> list:
        """Search for similar vectors in Pinecone."""
        try:
            search_params = {
                "vector": embedding,
                "top_k": top_k,
                "include_metadata": True,
                "include_values": False
            }
            
            if filter_dict:
                search_params["filter"] = filter_dict
            
            results = self.index.query(**search_params)
            return results.matches
        except Exception as e:
            logger.error(f"Pinecone search failed: {e}")
            raise e
    
    def test_connection(self) -> bool:
        """Test Pinecone connection."""
        try:
            stats = self.index.describe_index_stats()
            logger.info(f"Pinecone connection test passed. Index stats: {stats}")
            return True
        except Exception as e:
            logger.error(f"Pinecone connection test failed: {e}")
            return False


class OpenAIManager:
    """Manages OpenAI API connections and requests."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")
        
        openai.api_key = self.api_key
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1500"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using OpenAI API."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant designed to analyze legal and policy documents with high accuracy and provide clear, well-reasoned answers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise e
    
    def test_connection(self) -> bool:
        """Test OpenAI API connection."""
        try:
            # Simple test with minimal tokens
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt="Test",
                max_tokens=1
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False


class EmbeddingManager:
    """Manages sentence transformer model for generating embeddings."""
    
    def __init__(self):
        self.model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Embedding model '{self.model_name}' loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise e
    
    def encode(self, text: str) -> list:
        """Generate embedding for input text."""
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise e
    
    def encode_batch(self, texts: list) -> list:
        """Generate embeddings for multiple texts."""
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise e


# Global instances (singletons)
_database_manager: Optional[DatabaseManager] = None
_pinecone_manager: Optional[PineconeManager] = None
_openai_manager: Optional[OpenAIManager] = None
_embedding_manager: Optional[EmbeddingManager] = None


@lru_cache()
def get_database_manager() -> DatabaseManager:
    """Get database manager instance."""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager


@lru_cache()
def get_pinecone_manager() -> PineconeManager:
    """Get Pinecone manager instance."""
    global _pinecone_manager
    if _pinecone_manager is None:
        _pinecone_manager = PineconeManager()
    return _pinecone_manager


@lru_cache()
def get_openai_manager() -> OpenAIManager:
    """Get OpenAI manager instance."""
    global _openai_manager
    if _openai_manager is None:
        _openai_manager = OpenAIManager()
    return _openai_manager


@lru_cache()
def get_embedding_manager() -> EmbeddingManager:
    """Get embedding manager instance."""
    global _embedding_manager
    if _embedding_manager is None:
        _embedding_manager = EmbeddingManager()
    return _embedding_manager


def get_db_session():
    """FastAPI dependency for database sessions."""
    db_manager = get_database_manager()
    db = db_manager.get_db()
    try:
        yield db
    finally:
        db_manager.close_db(db)


async def check_service_health() -> Dict[str, str]:
    """Check health of all external services."""
    health_status = {}
    
    # Check database
    try:
        db_manager = get_database_manager()
        health_status["database"] = "healthy" if db_manager.test_connection() else "unhealthy"
    except Exception:
        health_status["database"] = "unhealthy"
    
    # Check Pinecone
    try:
        pinecone_manager = get_pinecone_manager()
        health_status["pinecone"] = "healthy" if pinecone_manager.test_connection() else "unhealthy"
    except Exception:
        health_status["pinecone"] = "unhealthy"
    
    # Check OpenAI
    try:
        openai_manager = get_openai_manager()
        health_status["openai"] = "healthy" if openai_manager.test_connection() else "unhealthy"
    except Exception:
        health_status["openai"] = "unhealthy"
    
    # Check embedding model (always healthy if loaded)
    try:
        get_embedding_manager()
        health_status["embedding_model"] = "healthy"
    except Exception:
        health_status["embedding_model"] = "unhealthy"
    
    return health_status
