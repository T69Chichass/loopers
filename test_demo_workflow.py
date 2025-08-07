"""
Test the complete document workflow with the demo system.
"""
import requests
import time
import json

def test_complete_workflow():
    """Test the complete document upload and query workflow."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Complete Document Query Workflow\n")
    
    # Step 1: Check system status
    print("1️⃣ Checking system status...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            info = response.json()
            print(f"   ✅ {info['name']}")
            print(f"   📝 Mode: {info.get('status', 'Demo mode')}")
        else:
            print(f"   ❌ Server not responding: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return
    
    # Step 2: Create sample document
    print("\n2️⃣ Creating sample policy document...")
    sample_policy = """
    CORPORATE INSURANCE POLICY
    
    COVERAGE DETAILS:
    This policy provides comprehensive health insurance coverage for employees.
    
    COVERED SERVICES:
    1. Medical Services - Physician visits, specialist consultations
    2. Surgical Procedures - Outpatient and inpatient surgery including knee surgery
    3. Emergency Services - Emergency room visits covered 24/7
    4. Preventive Care - Annual physical exams and vaccinations
    
    DEDUCTIBLES:
    - Annual deductible: $1,500 per individual
    - Emergency room copay: $200
    - Specialist visit copay: $50
    
    CLAIMS PROCESS:
    1. Obtain pre-authorization for non-emergency procedures
    2. Submit claims within 90 days of service
    3. Include all required documentation
    
    EXCLUSIONS:
    - Cosmetic surgery (unless medically necessary)
    - Experimental treatments
    """
    
    # Step 3: Upload document
    print("\n3️⃣ Uploading sample document...")
    try:
        files = {'file': ('sample_policy.txt', sample_policy.encode(), 'text/plain')}
        data = {
            'document_type': 'insurance',
            'category': 'health_insurance',
            'title': 'Sample Health Insurance Policy'
        }
        
        response = requests.post(
            f"{base_url}/documents/upload",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            upload_result = response.json()
            print(f"   ✅ Document uploaded successfully!")
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
    
    # Step 4: List documents
    print("\n4️⃣ Checking uploaded documents...")
    try:
        response = requests.get(f"{base_url}/documents")
        if response.status_code == 200:
            docs = response.json()
            print(f"   ✅ Found {docs['total_count']} document(s)")
            for doc in docs['documents'][:3]:  # Show first 3
                print(f"   📄 {doc['title']} ({doc['document_type']})")
        else:
            print(f"   ❌ Failed to list documents: {response.status_code}")
    except Exception as e:
        print(f"   ❌ List error: {e}")
    
    # Step 5: Test various queries
    print("\n5️⃣ Testing document queries...")
    
    test_queries = [
        "Does this policy cover knee surgery?",
        "What is the annual deductible?", 
        "How do I file a claim?",
        "Are emergency room visits covered?",
        "What procedures require pre-authorization?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: '{query}'")
        try:
            response = requests.post(
                f"{base_url}/query",
                json={'query': query}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Answer: {result['answer'][:100]}...")
                print(f"   🎯 Confidence: {result['confidence']}")
                print(f"   📚 Supporting clauses: {len(result['supporting_clauses'])}")
                
                # Show first supporting clause
                if result['supporting_clauses']:
                    clause = result['supporting_clauses'][0]
                    print(f"   📝 Evidence: {clause['text'][:80]}...")
            else:
                print(f"   ❌ Query failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Query error: {e}")
        
        time.sleep(0.5)  # Small delay between queries
    
    # Step 6: Test health check
    print("\n6️⃣ Checking system health...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ System status: {health['status']}")
            print(f"   📊 Documents uploaded: {health.get('documents_uploaded', 0)}")
            print(f"   🧩 Chunks created: {health.get('chunks_created', 0)}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    print("\n" + "="*60)
    print("🎉 Document Query Workflow Test Complete!")
    print("\nWhat you just tested:")
    print("✅ Document upload and processing")
    print("✅ Text extraction and chunking") 
    print("✅ Document management and listing")
    print("✅ Natural language querying")
    print("✅ AI-powered answer generation")
    print("✅ Supporting evidence extraction")
    print("✅ System health monitoring")
    
    print("\n🚀 Next steps for full system:")
    print("1. Set up PostgreSQL database")
    print("2. Configure Pinecone vector database") 
    print("3. Add OpenAI API key")
    print("4. Run: python main.py")
    print("5. Upload real policy documents")
    print("6. Start querying with real AI!")

if __name__ == "__main__":
    test_complete_workflow()
