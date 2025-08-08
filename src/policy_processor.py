#!/usr/bin/env python3
"""
Policy Document Processor - Clean and organized version.
Handles document download, upload, and query processing.
"""

import requests
import json
import time
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Data class for query results."""
    question: str
    answer: str
    confidence: str
    supporting_clauses_count: int
    query_id: str
    timestamp: str


@dataclass
class DocumentInfo:
    """Data class for document information."""
    document_id: str
    title: str
    text_length: int
    chunk_count: int
    processing_time: float


class PolicyProcessor:
    """Main class for processing policy documents and queries."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
    
    def download_document(self, url: str) -> Optional[Path]:
        """Download document from URL."""
        logger.info(f"Downloading document from: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(response.content)
                tmp_path = Path(tmp_file.name)
            
            logger.info(f"Document downloaded successfully: {tmp_path}")
            return tmp_path
            
        except Exception as e:
            logger.error(f"Failed to download document: {e}")
            return None
    
    def upload_document(self, file_path: Path, title: str, 
                       document_type: str = "insurance", 
                       category: str = "health_insurance") -> Optional[DocumentInfo]:
        """Upload document to API."""
        logger.info(f"Uploading document: {title}")
        
        try:
            with open(file_path, 'rb') as pdf_file:
                files = {
                    'file': ('policy.pdf', pdf_file, 'application/pdf')
                }
                
                data = {
                    'document_type': document_type,
                    'category': category,
                    'title': title
                }
                
                response = self.session.post(
                    f"{self.base_url}/documents/upload",
                    files=files,
                    data=data
                )
                response.raise_for_status()
                
                result = response.json()
                document_info = DocumentInfo(
                    document_id=result['document_id'],
                    title=result['title'],
                    text_length=result['text_length'],
                    chunk_count=result['chunk_count'],
                    processing_time=result['processing_time']
                )
                
                logger.info(f"Document uploaded successfully: {document_info.document_id}")
                return document_info
                
        except Exception as e:
            logger.error(f"Failed to upload document: {e}")
            return None
    
    def process_query(self, question: str) -> Optional[QueryResult]:
        """Process a single query."""
        try:
            response = self.session.post(
                f"{self.base_url}/query",
                json={'query': question}
            )
            response.raise_for_status()
            
            result = response.json()
            query_result = QueryResult(
                question=question,
                answer=result['answer'],
                confidence=result['confidence'],
                supporting_clauses_count=len(result['supporting_clauses']),
                query_id=result['query_id'],
                timestamp=result['timestamp']
            )
            
            return query_result
            
        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            return None
    
    def process_queries(self, questions: List[str]) -> List[QueryResult]:
        """Process multiple queries."""
        logger.info(f"Processing {len(questions)} queries")
        
        results = []
        for i, question in enumerate(questions, 1):
            logger.info(f"Processing query {i}/{len(questions)}")
            
            result = self.process_query(question)
            if result:
                results.append(result)
            
            # Small delay between queries
            time.sleep(1)
        
        logger.info(f"Processed {len(results)}/{len(questions)} queries successfully")
        return results
    
    def save_results(self, document_info: DocumentInfo, 
                    results: List[QueryResult], 
                    output_file: str = "policy_query_results.json") -> bool:
        """Save results to JSON file."""
        try:
            output_data = {
                'document_id': document_info.document_id,
                'document_title': document_info.title,
                'total_questions': len(results),
                'processed_questions': len(results),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'results': [
                    {
                        'question': r.question,
                        'answer': r.answer,
                        'confidence': r.confidence,
                        'supporting_clauses_count': r.supporting_clauses_count,
                        'query_id': r.query_id,
                        'timestamp': r.timestamp
                    }
                    for r in results
                ]
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return False
    
    def process_policy_document(self, document_url: str, questions: List[str], 
                               title: str = "Policy Document") -> bool:
        """Complete workflow: download, upload, and process queries."""
        logger.info("Starting policy document processing workflow")
        
        # Step 1: Download document
        tmp_path = self.download_document(document_url)
        if not tmp_path:
            return False
        
        try:
            # Step 2: Upload document
            document_info = self.upload_document(tmp_path, title)
            if not document_info:
                return False
            
            # Step 3: Process queries
            results = self.process_queries(questions)
            
            # Step 4: Save results
            success = self.save_results(document_info, results)
            
            # Print summary
            self._print_summary(document_info, results)
            
            return success
            
        finally:
            # Clean up temporary file
            tmp_path.unlink(missing_ok=True)
    
    def _print_summary(self, document_info: DocumentInfo, results: List[QueryResult]):
        """Print processing summary."""
        print("\n" + "="*60)
        print("🎉 Policy Processing Complete!")
        print("="*60)
        print(f"📄 Document: {document_info.title}")
        print(f"🆔 Document ID: {document_info.document_id}")
        print(f"📊 Text Length: {document_info.text_length:,} characters")
        print(f"🧩 Chunks Created: {document_info.chunk_count}")
        print(f"⏱️ Processing Time: {document_info.processing_time:.3f}s")
        print(f"❓ Questions Processed: {len(results)}")
        print(f"🎯 High Confidence: {sum(r.confidence == 'high' for r in results)}/{len(results)}")
        print("="*60)


def main():
    """Main function with example usage."""
    # Example questions
    questions = [
        "What is the grace period for premium payment?",
        "What is the waiting period for pre-existing diseases?",
        "Does this policy cover maternity expenses?",
        "What is the waiting period for cataract surgery?",
        "Are organ donor expenses covered?",
        "What is the No Claim Discount offered?",
        "Is there a benefit for preventive health check-ups?",
        "How does the policy define a 'Hospital'?",
        "What is the coverage for AYUSH treatments?",
        "Are there sub-limits on room rent and ICU charges?"
    ]
    
    # Example document URL (replace with your actual URL)
    document_url = "https://example.com/policy.pdf"
    
    # Initialize processor
    processor = PolicyProcessor()
    
    # Process document
    success = processor.process_policy_document(document_url, questions, "Example Policy")
    
    if success:
        print("✅ Processing completed successfully!")
    else:
        print("❌ Processing failed!")


if __name__ == "__main__":
    main()
