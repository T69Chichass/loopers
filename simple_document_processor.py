"""
Simple document processor for handling PDF documents without heavy dependencies.
"""
import logging
import tempfile
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    try:
        import pypdf
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False
        logger.warning("PyPDF2/pypdf not available - PDF processing will be limited")

try:
    import fitz  # PyMuPDF
    MUPDF_AVAILABLE = True
except ImportError:
    MUPDF_AVAILABLE = False
    logger.warning("PyMuPDF not available - using fallback PDF processing")


class SimpleDocumentProcessor:
    """Simple document processor for basic text extraction."""
    
    def __init__(self):
        self.supported_extensions = {'.pdf', '.txt'}
    
    async def download_document(self, url: str) -> str:
        """Download document from URL and save to temporary file."""
        try:
            logger.info(f"Downloading document from: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            logger.info(f"Document downloaded to: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to download document: {e}")
            raise Exception(f"Failed to download document from {url}: {str(e)}")
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using available libraries."""
        try:
            if MUPDF_AVAILABLE:
                return self._extract_with_mupdf(file_path)
            elif PDF_AVAILABLE:
                return self._extract_with_pypdf(file_path)
            else:
                raise Exception("No PDF processing library available")
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise
    
    def _extract_with_mupdf(self, file_path: str) -> str:
        """Extract text using PyMuPDF (fitz)."""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            raise
    
    def _extract_with_pypdf(self, file_path: str) -> str:
        """Extract text using PyPDF2/pypdf."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                if 'pypdf' in globals():
                    reader = pypdf.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                else:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"PyPDF extraction failed: {e}")
            raise
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', ' ', text)
        
        # Normalize spacing around punctuation
        text = re.sub(r'\s+([\.\,\;\:\!\?])', r'\1', text)
        
        return text.strip()
    
    def split_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks."""
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    async def process_document_from_url(self, url: str) -> Dict[str, Any]:
        """Process document from URL and return extracted text and chunks."""
        temp_path = None
        try:
            # Download document
            temp_path = await self.download_document(url)
            
            # Determine file type
            file_extension = Path(temp_path).suffix.lower()
            
            # Extract text
            if file_extension == '.pdf':
                text = self.extract_text_from_pdf(temp_path)
            elif file_extension == '.txt':
                text = self.extract_text_from_txt(temp_path)
            else:
                raise Exception(f"Unsupported file type: {file_extension}")
            
            # Clean text
            cleaned_text = self.clean_text(text)
            
            # Split into chunks
            chunks = self.split_into_chunks(cleaned_text)
            
            logger.info(f"Processed document: {len(cleaned_text)} characters, {len(chunks)} chunks")
            
            return {
                'text': cleaned_text,
                'chunks': chunks,
                'chunk_count': len(chunks),
                'text_length': len(cleaned_text)
            }
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise
        finally:
            # Clean up temporary file
            if temp_path and Path(temp_path).exists():
                try:
                    Path(temp_path).unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {temp_path}: {e}")


# Global instance
_document_processor: Optional[SimpleDocumentProcessor] = None

def get_document_processor() -> SimpleDocumentProcessor:
    """Get document processor instance."""
    global _document_processor
    if _document_processor is None:
        _document_processor = SimpleDocumentProcessor()
    return _document_processor
