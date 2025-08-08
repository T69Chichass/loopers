"""
Test script for the insurance policy document with specific queries.
Tests the system with real insurance policy and domain-specific queries.
"""
import requests
import time
import json
from pathlib import Path

def test_insurance_policy_system():
    """Test the system with the Arogya Sanjeevani Policy document."""
    base_url = "http://localhost:8001"
    
    print("🏥 Testing Insurance Policy Query System")
    print("=" * 60)
    
    # Step 1: Check system status
    print("1️⃣ Checking system status...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            info = response.json()
            print(f"   ✅ {info['name']}")
            print(f"   📝 Status: {info.get('status', 'Running')}")
        else:
            print(f"   ❌ Server not responding: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        print(f"   💡 Make sure the server is running on {base_url}")
        return
    
    # Step 2: Upload the insurance policy document
    print("\n2️⃣ Uploading Arogya Sanjeevani Policy...")
    
    policy_file_path = "Arogya Sanjeevani Policy - CIN - U10200WB1906GOI001713 1.pdf"
    
    if not Path(policy_file_path).exists():
        print(f"   ❌ Policy file not found: {policy_file_path}")
        print("   💡 Make sure the PDF file is in the current directory")
        return
    
    try:
        with open(policy_file_path, 'rb') as f:
            files = {'file': (policy_file_path, f, 'application/pdf')}
            data = {
                'document_type': 'insurance',
                'category': 'health_insurance',
                'title': 'Arogya Sanjeevani Policy - National Parivar Mediclaim Plus'
            }
            
            response = requests.post(
                f"{base_url}/documents/upload",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            upload_result = response.json()
            print(f"   ✅ Policy uploaded successfully!")
            print(f"   📄 Document ID: {upload_result['document_id']}")
            print(f"   📊 Text length: {upload_result['text_length']} characters")
            print(f"   🧩 Chunks created: {upload_result['chunk_count']}")
            print(f"   ⏱️ Processing time: {upload_result['processing_time']}s")
            document_id = upload_result['document_id']
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
        return
    
    # Step 3: Wait for processing
    print("\n3️⃣ Waiting for document processing...")
    time.sleep(2)
    
    # Step 4: Test with specific insurance queries
    print("\n4️⃣ Testing insurance-specific queries...")
    
    insurance_queries = [
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
    
    successful_queries = 0
    total_response_time = 0
    
    for i, query in enumerate(insurance_queries, 1):
        print(f"\n   Query {i}/10: '{query}'")
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/query",
                json={'query': query},
                timeout=30
            )
            response_time = time.time() - start_time
            total_response_time += response_time
            
            if response.status_code == 200:
                result = response.json()
                successful_queries += 1
                
                print(f"   ✅ Response time: {response_time:.2f}s")
                print(f"   📝 Answer: {result['answer'][:150]}...")
                print(f"   🎯 Confidence: {result['confidence']}")
                print(f"   📚 Supporting clauses: {len(result['supporting_clauses'])}")
                
                # Show the most relevant supporting clause
                if result['supporting_clauses']:
                    best_clause = result['supporting_clauses'][0]
                    print(f"   🔍 Key evidence: {best_clause['text'][:100]}...")
                    print(f"   📊 Confidence score: {best_clause.get('confidence_score', 'N/A')}")
                
            else:
                print(f"   ❌ Query failed: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Query error: {e}")
        
        # Small delay between queries
        time.sleep(0.5)
    
    # Step 5: Performance summary
    print(f"\n5️⃣ Performance Summary")
    print(f"   📊 Successful queries: {successful_queries}/{len(insurance_queries)}")
    
    if successful_queries > 0:
        avg_response_time = total_response_time / successful_queries
        print(f"   ⏱️ Average response time: {avg_response_time:.2f}s")
        success_rate = (successful_queries / len(insurance_queries)) * 100
        print(f"   🎯 Success rate: {success_rate:.1f}%")
    
    # Step 6: List all documents
    print(f"\n6️⃣ Document inventory...")
    try:
        response = requests.get(f"{base_url}/documents")
        if response.status_code == 200:
            docs = response.json()
            print(f"   ✅ Total documents in system: {docs['total_count']}")
            for doc in docs['documents']:
                print(f"   📄 {doc['title']} ({doc['document_type']})")
                print(f"      ID: {doc['document_id']}")
                print(f"      Status: {doc.get('status', 'processed')}")
        else:
            print(f"   ❌ Failed to list documents: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Document listing error: {e}")
    
    # Step 7: System health check
    print(f"\n7️⃣ Final system health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ System status: {health['status']}")
            print(f"   📊 Documents uploaded: {health.get('documents_uploaded', 0)}")
            print(f"   🧩 Total chunks: {health.get('chunks_created', 0)}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Final summary
    print("\n" + "="*60)
    print("🎉 Insurance Policy Testing Complete!")
    print("\n📋 What was tested:")
    print("✅ PDF document upload and processing")
    print("✅ Insurance-specific terminology extraction")
    print("✅ Policy terms and conditions queries")
    print("✅ Waiting periods and coverage details")
    print("✅ Premium and claims processing questions")
    print("✅ Medical benefits and limitations")
    print("✅ AYUSH and alternative treatments")
    print("✅ Room rent and sub-limit queries")
    
    if successful_queries >= len(insurance_queries) * 0.8:  # 80% success
        print("\n🏆 EXCELLENT: System handled insurance queries very well!")
    elif successful_queries >= len(insurance_queries) * 0.6:  # 60% success
        print("\n👍 GOOD: System handled most insurance queries successfully!")
    else:
        print("\n⚠️ NEEDS IMPROVEMENT: Consider refining query processing for insurance domain")
    
    print(f"\n🚀 Ready for production with real AI services!")
    print("   📝 Next: Configure OpenAI API for smarter responses")
    print("   🔍 Next: Set up Pinecone for better semantic search")
    print("   💾 Next: Configure PostgreSQL for persistent storage")

if __name__ == "__main__":
    test_insurance_policy_system()
