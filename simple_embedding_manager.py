"""
Simple embedding manager that provides fallback embeddings when sentence-transformers is not available.
"""
import logging
import hashlib
import random
from typing import List, Optional

logger = logging.getLogger(__name__)

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    logger.info("Sentence transformers available")
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("Sentence transformers not available - using dummy embeddings")


class SimpleEmbeddingManager:
    """Simple embedding manager with fallback to dummy embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.embedding_size = 384  # Standard size for all-MiniLM-L6-v2
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info(f"Initializing sentence transformer model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                logger.info("Sentence transformer model initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize sentence transformer model: {e}")
                logger.warning("Falling back to dummy embeddings")
                self.model = None
        else:
            logger.warning("Sentence transformers not available - using dummy embeddings")
            self.model = None
    
    def _generate_dummy_embedding(self, text: str) -> List[float]:
        """Generate a deterministic dummy embedding based on text content."""
        # Create a hash of the text to make embeddings deterministic
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Use the hash to seed a random number generator
        random.seed(text_hash)
        
        # Generate a list of random floats between -1 and 1
        embedding = [random.uniform(-1.0, 1.0) for _ in range(self.embedding_size)]
        
        # Normalize the embedding to unit length
        magnitude = sum(x * x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    def encode(self, text: str) -> List[float]:
        """Generate embedding for input text."""
        try:
            if self.model is not None:
                # Use real sentence transformer
                embedding = self.model.encode(text, convert_to_tensor=False)
                return embedding.tolist()
            else:
                # Use dummy embedding
                return self._generate_dummy_embedding(text)
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Return dummy embedding on error
            return self._generate_dummy_embedding(text)
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            if self.model is not None:
                # Use real sentence transformer
                embeddings = self.model.encode(texts, convert_to_tensor=False)
                return [emb.tolist() for emb in embeddings]
            else:
                # Use dummy embeddings
                return [self._generate_dummy_embedding(text) for text in texts]
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            # Return dummy embeddings on error
            return [self._generate_dummy_embedding(text) for text in texts]
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            if len(embedding1) != len(embedding2):
                return 0.0
            
            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            
            # Calculate magnitudes
            mag1 = sum(a * a for a in embedding1) ** 0.5
            mag2 = sum(b * b for b in embedding2) ** 0.5
            
            # Calculate cosine similarity
            if mag1 > 0 and mag2 > 0:
                return dot_product / (mag1 * mag2)
            else:
                return 0.0
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def find_similar_chunks(self, query_embedding: List[float], chunk_embeddings: List[List[float]], top_k: int = 5) -> List[tuple]:
        """Find the most similar chunks to the query."""
        try:
            similarities = []
            for i, chunk_embedding in enumerate(chunk_embeddings):
                similarity = self.similarity(query_embedding, chunk_embedding)
                similarities.append((i, similarity))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Return top_k results
            return similarities[:top_k]
        except Exception as e:
            logger.error(f"Failed to find similar chunks: {e}")
            return []


# Global instance
_embedding_manager: Optional[SimpleEmbeddingManager] = None

def get_simple_embedding_manager() -> SimpleEmbeddingManager:
    """Get simple embedding manager instance."""
    global _embedding_manager
    if _embedding_manager is None:
        _embedding_manager = SimpleEmbeddingManager()
    return _embedding_manager
