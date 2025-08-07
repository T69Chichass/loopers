"""
Test script for document processing functionality.
Creates sample documents and tests the complete pipeline.
"""
import asyncio
import json
import tempfile
import time
from pathlib import Path
from typing import Dict, Any
import httpx

# Create sample documents for testing
def create_sample_documents():
    """Create sample policy documents for testing."""
    samples = {}
    
    # Sample insurance policy
    insurance_content = """
    CORPORATE HEALTH INSURANCE POLICY
    
    COVERAGE DETAILS:
    This policy provides comprehensive health coverage for employees and their dependents.
    
    COVERED SERVICES:
    1. Medical Services
       - Physician visits
       - Specialist consultations
       - Emergency room visits
       - Urgent care visits
    
    2. Surgical Procedures
       - Outpatient surgery
       - Inpatient surgery
       - Orthopedic procedures including knee surgery, hip surgery
       - Cardiac procedures
    
    3. Preventive Care
       - Annual physical exams
       - Vaccinations
       - Cancer screenings
       - Mammograms
    
    4. Mental Health Services
       - Therapy sessions
       - Psychiatric consultations
       - Substance abuse treatment
    
    DEDUCTIBLES AND COPAYS:
    - Annual deductible: $1,500 per individual, $3,000 per family
    - Physician visit copay: $25
    - Specialist visit copay: $50
    - Emergency room copay: $200
    
    EXCLUSIONS:
    - Cosmetic surgery (unless medically necessary)
    - Experimental treatments
    - Alternative medicine not approved by FDA
    
    CLAIMS PROCESS:
    1. Obtain pre-authorization for non-emergency procedures
    2. Submit claims within 90 days of service
    3. Include all required documentation
    4. Claims processed within 30 days
    
    APPEALS PROCESS:
    If a claim is denied, members have 60 days to file an appeal.
    Appeals are reviewed by an independent medical review board.
    """
    
    # Sample HR policy
    hr_content = """
    EMPLOYEE HANDBOOK
    
    VACATION POLICY:
    - New employees: 10 days per year
    - 2-5 years service: 15 days per year
    - 5+ years service: 20 days per year
    - Maximum carryover: 5 days to next year
    
    SICK LEAVE POLICY:
    - All employees receive 8 sick days per year
    - Unused sick days do not carry over
    - Medical documentation required for absences over 3 days
    
    WORK FROM HOME POLICY:
    - Employees may work from home up to 2 days per week
    - Manager approval required
    - Home office must meet safety standards
    - Equipment provided by company
    
    PROFESSIONAL DEVELOPMENT:
    - Annual training budget: $2,000 per employee
    - Conference attendance encouraged
    - Tuition reimbursement available
    - Skills development programs offered quarterly
    
    DISCIPLINARY POLICY:
    1. Verbal warning
    2. Written warning
    3. Final written warning
    4. Termination
    
    Serious misconduct may result in immediate termination.
    
    HARASSMENT POLICY:
    - Zero tolerance for harassment
    - Report incidents to HR immediately
    - Anonymous reporting available
    - All reports investigated thoroughly
    """
    
    # Sample legal contract
    legal_content = """
    SERVICE AGREEMENT
    
    PAYMENT TERMS:
    - Net 30 payment terms
    - Late fees: 1.5% per month on overdue amounts
    - Payment methods: Check, wire transfer, ACH
    
    TERMINATION CONDITIONS:
    Either party may terminate this agreement with 30 days written notice.
    
    Immediate termination allowed for:
    - Breach of contract
    - Non-payment after 60 days
    - Violation of confidentiality terms
    
    LIABILITY LIMITATIONS:
    - Total liability limited to contract value
    - No liability for indirect or consequential damages
    - Indemnification required for third-party claims
    
    CONFIDENTIALITY:
    - All proprietary information must remain confidential
    - Non-disclosure period: 5 years after agreement termination
    - Return of materials required upon termination
    
    DISPUTE RESOLUTION:
    - Disputes resolved through binding arbitration
    - Governed by laws of State of California
    - Venue: San Francisco County
    
    FORCE MAJEURE:
    Performance excused during force majeure events including:
    - Natural disasters
    - Government actions
    - Labor strikes
    - Pandemics
    """
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(insurance_content)
        samples['insurance'] = {
            'path': f.name,
            'type': 'insurance',
            'category': 'health_insurance',
            'title': 'Corporate Health Insurance Policy'
        }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(hr_content)
        samples['hr'] = {
            'path': f.name,
            'type': 'hr',
            'category': 'policies',
            'title': 'Employee Handbook'
        }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(legal_content)
        samples['legal'] = {
            'path': f.name,
            'type': 'legal',
            'category': 'contracts',
            'title': 'Service Agreement'
        }
    
    return samples


class DocumentProcessingTester:
    """Test runner for document processing functionality."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60)  # Longer timeout for processing
        self.uploaded_documents = []
    
    async def test_document_upload(self, sample_docs: Dict[str, Dict]) -> Dict[str, Any]:
        """Test document upload functionality."""
        print("🔍 Testing document upload...")
        results = []
        
        for doc_name, doc_info in sample_docs.items():
            try:
                print(f"   Uploading {doc_name} document...")
                
                with open(doc_info['path'], 'rb') as f:
                    files = {'file': (f"{doc_name}.txt", f, 'text/plain')}
                    data = {
                        'document_type': doc_info['type'],
                        'category': doc_info['category'],
                        'title': doc_info['title']
                    }
                    
                    start_time = time.time()
                    response = await self.client.post(
                        f"{self.base_url}/documents/upload",
                        files=files,
                        data=data
                    )
                    upload_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    self.uploaded_documents.append(result['document_id'])
                    
                    print(f"   ✅ {doc_name} uploaded successfully")
                    print(f"      Document ID: {result['document_id']}")
                    print(f"      Chunks created: {result['chunk_count']}")
                    print(f"      Processing time: {result['processing_time']:.2f}s")
                    
                    results.append({
                        'document_type': doc_name,
                        'success': True,
                        'document_id': result['document_id'],
                        'upload_time': upload_time,
                        'processing_time': result['processing_time'],
                        'chunk_count': result['chunk_count']
                    })
                else:
                    print(f"   ❌ {doc_name} upload failed: {response.status_code}")
                    print(f"      Error: {response.text}")
                    results.append({
                        'document_type': doc_name,
                        'success': False,
                        'error': response.text
                    })
                    
            except Exception as e:
                print(f"   ❌ {doc_name} upload error: {e}")
                results.append({
                    'document_type': doc_name,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'test_name': 'document_upload',
            'results': results,
            'overall_success': all(r.get('success', False) for r in results)
        }
    
    async def test_document_list(self) -> Dict[str, Any]:
        """Test document listing functionality."""
        print("\n🔍 Testing document listing...")
        
        try:
            response = await self.client.get(f"{self.base_url}/documents")
            
            if response.status_code == 200:
                result = response.json()
                document_count = len(result['documents'])
                total_count = result['total_count']
                
                print(f"   ✅ Document list retrieved successfully")
                print(f"      Documents returned: {document_count}")
                print(f"      Total documents: {total_count}")
                
                return {
                    'test_name': 'document_list',
                    'success': True,
                    'document_count': document_count,
                    'total_count': total_count
                }
            else:
                print(f"   ❌ Document list failed: {response.status_code}")
                return {
                    'test_name': 'document_list',
                    'success': False,
                    'error': response.text
                }
                
        except Exception as e:
            print(f"   ❌ Document list error: {e}")
            return {
                'test_name': 'document_list',
                'success': False,
                'error': str(e)
            }
    
    async def test_document_queries(self) -> Dict[str, Any]:
        """Test querying uploaded documents."""
        print("\n🔍 Testing document queries...")
        
        test_queries = [
            {
                'query': 'Does the insurance policy cover knee surgery?',
                'expected_content': ['knee surgery', 'orthopedic', 'covered']
            },
            {
                'query': 'What is the vacation policy for new employees?',
                'expected_content': ['10 days', 'new employees', 'vacation']
            },
            {
                'query': 'What are the payment terms in the contract?',
                'expected_content': ['Net 30', 'payment terms', 'late fees']
            },
            {
                'query': 'How do I file a claim for medical expenses?',
                'expected_content': ['claims', 'submit', 'documentation']
            },
            {
                'query': 'What is the work from home policy?',
                'expected_content': ['work from home', '2 days', 'manager approval']
            }
        ]
        
        results = []
        
        for test_case in test_queries:
            try:
                print(f"   Testing query: '{test_case['query']}'")
                
                start_time = time.time()
                response = await self.client.post(
                    f"{self.base_url}/query",
                    json={'query': test_case['query']}
                )
                query_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get('answer', '').lower()
                    
                    # Check if expected content is in the answer
                    content_found = sum(
                        1 for content in test_case['expected_content']
                        if content.lower() in answer
                    )
                    
                    success = content_found > 0 and len(result.get('supporting_clauses', [])) > 0
                    
                    if success:
                        print(f"   ✅ Query answered successfully ({query_time:.2f}s)")
                        print(f"      Confidence: {result.get('confidence', 'unknown')}")
                        print(f"      Supporting clauses: {len(result.get('supporting_clauses', []))}")
                    else:
                        print(f"   ⚠️ Query answered but quality may be low")
                        print(f"      Expected content found: {content_found}/{len(test_case['expected_content'])}")
                    
                    results.append({
                        'query': test_case['query'],
                        'success': success,
                        'query_time': query_time,
                        'confidence': result.get('confidence'),
                        'supporting_clauses': len(result.get('supporting_clauses', [])),
                        'content_relevance': content_found / len(test_case['expected_content'])
                    })
                else:
                    print(f"   ❌ Query failed: {response.status_code}")
                    results.append({
                        'query': test_case['query'],
                        'success': False,
                        'error': response.text
                    })
                    
            except Exception as e:
                print(f"   ❌ Query error: {e}")
                results.append({
                    'query': test_case['query'],
                    'success': False,
                    'error': str(e)
                })
        
        successful_queries = sum(1 for r in results if r.get('success', False))
        avg_response_time = sum(r.get('query_time', 0) for r in results) / len(results) if results else 0
        
        return {
            'test_name': 'document_queries',
            'results': results,
            'successful_queries': successful_queries,
            'total_queries': len(test_queries),
            'success_rate': successful_queries / len(test_queries) if test_queries else 0,
            'average_response_time': avg_response_time,
            'overall_success': successful_queries >= len(test_queries) * 0.6  # 60% success threshold
        }
    
    async def cleanup_documents(self):
        """Clean up uploaded test documents."""
        print("\n🧹 Cleaning up test documents...")
        
        for doc_id in self.uploaded_documents:
            try:
                response = await self.client.delete(f"{self.base_url}/documents/{doc_id}")
                if response.status_code == 200:
                    print(f"   ✅ Deleted document: {doc_id}")
                else:
                    print(f"   ⚠️ Failed to delete document: {doc_id}")
            except Exception as e:
                print(f"   ❌ Error deleting document {doc_id}: {e}")
    
    async def run_full_test(self) -> Dict[str, Any]:
        """Run complete document processing test suite."""
        print("🚀 Starting Document Processing Tests...\n")
        start_time = time.time()
        
        # Create sample documents
        print("📝 Creating sample documents...")
        sample_docs = create_sample_documents()
        
        test_results = {}
        
        try:
            # Test document upload
            test_results['upload'] = await self.test_document_upload(sample_docs)
            
            # Wait a moment for processing to complete
            print("\n⏳ Waiting for document processing to complete...")
            await asyncio.sleep(2)
            
            # Test document listing
            test_results['list'] = await self.test_document_list()
            
            # Test queries (only if uploads were successful)
            if test_results['upload']['overall_success']:
                test_results['queries'] = await self.test_document_queries()
            else:
                print("\n⚠️ Skipping query tests due to upload failures")
                test_results['queries'] = {
                    'test_name': 'document_queries',
                    'skipped': True,
                    'reason': 'Upload failures'
                }
            
        except Exception as e:
            print(f"\n💥 Test execution error: {e}")
            test_results['error'] = str(e)
        
        finally:
            # Cleanup
            await self.cleanup_documents()
            
            # Clean up sample files
            for doc_info in sample_docs.values():
                try:
                    Path(doc_info['path']).unlink()
                except Exception:
                    pass
        
        total_time = time.time() - start_time
        
        # Summary
        print(f"\n📊 Document Processing Test Summary (Total time: {total_time:.2f}s)")
        print("=" * 60)
        
        for test_name, result in test_results.items():
            if isinstance(result.get('overall_success'), bool):
                status = "✅ PASSED" if result['overall_success'] else "❌ FAILED"
                print(f"{status} {test_name}")
            elif result.get('skipped'):
                print(f"⏭️ SKIPPED {test_name}: {result.get('reason', 'Unknown')}")
        
        await self.client.aclose()
        
        return {
            'total_time': total_time,
            'detailed_results': test_results
        }


async def main():
    """Main test execution function."""
    tester = DocumentProcessingTester()
    results = await tester.run_full_test()
    return results


if __name__ == "__main__":
    print("🧪 Document Processing Test Suite")
    print("=" * 60)
    print("Make sure the API server is running on http://localhost:8000")
    print("And that all services (PostgreSQL, Pinecone, OpenAI) are configured\n")
    
    try:
        results = asyncio.run(main())
        print("\n🎉 Document processing tests completed!")
        
    except KeyboardInterrupt:
        print("\n\n⛔ Tests interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        exit(1)
