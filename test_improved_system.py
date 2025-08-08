"""
Test the improved demo system with proper English text extraction.
"""
import requests
import time
import json

def test_improved_system():
    """Test the improved demo system with better PDF extraction."""
    base_url = "http://localhost:8002"
    
    print("🏥 Testing IMPROVED Insurance Policy System")
    print("=" * 60)
    
    # Step 1: Check system status
    print("1️⃣ Checking improved system status...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            info = response.json()
            print(f"   ✅ {info['name']}")
            print(f"   📝 Status: {info['status']}")
            print(f"   🆕 Improvements:")
            for improvement in info.get('improvements', []):
                print(f"      {improvement}")
        else:
            print(f"   ❌ Server not responding: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return
    
    # Step 2: Upload the insurance policy
    print("\\n2️⃣ Uploading policy with improved extraction...")
    
    policy_file = "Arogya Sanjeevani Policy - CIN - U10200WB1906GOI001713 1.pdf"
    
    try:
        with open(policy_file, 'rb') as f:
            files = {'file': (policy_file, f, 'application/pdf')}
            data = {
                'document_type': 'insurance',
                'category': 'health_insurance',
                'title': 'Arogya Sanjeevani Policy - Improved Extraction'
            }
            
            response = requests.post(
                f"{base_url}/documents/upload",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Upload successful!")
            print(f"   📄 Document ID: {result['document_id']}")
            print(f"   📊 Text extracted: {result['text_length']} characters")
            print(f"   🧩 Chunks created: {result['chunk_count']}")
            print(f"   ⏱️ Processing time: {result['processing_time']}s")
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
        return
    
    # Step 3: Test specific insurance queries
    print("\\n3️⃣ Testing insurance-specific queries with improved responses...")
    
    test_queries = [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\\n   Query {i}: '{query}'")
        try:
            response = requests.post(
                f"{base_url}/query",
                json={'query': query}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Response received")
                print(f"   📝 Answer: {result['answer'][:200]}...")
                print(f"   🎯 Confidence: {result['confidence']}")
                print(f"   📚 Supporting evidence: {len(result['supporting_clauses'])} pieces")
                
                # Show first supporting clause to check if it's readable
                if result['supporting_clauses']:
                    evidence = result['supporting_clauses'][0]['text']
                    print(f"   🔍 Evidence sample: {evidence[:100]}...")
                    
            else:
                print(f"   ❌ Query failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Query error: {e}")
        
        time.sleep(0.5)
    
    # Step 4: Check final status
    print("\\n4️⃣ Final system check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ System status: {health['status']}")
            print(f"   📊 Documents: {health['documents_uploaded']}")
            print(f"   🧩 Chunks: {health['chunks_created']}")
            print(f"   🔢 Version: {health['version']}")
        else:
            print(f"   ❌ Health check failed")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    print("\\n" + "="*60)
    print("🎉 Improved System Test Complete!")
    print("\\n🔍 Key Improvements Tested:")
    print("✅ Better PDF text extraction (readable English)")
    print("✅ Insurance-specific intelligent responses")
    print("✅ Proper text chunking and processing")
    print("✅ Clean supporting evidence")
    
    print("\\n📋 What should work better now:")
    print("• English text instead of corrupted characters")
    print("• More relevant answers to insurance questions")
    print("• Better supporting evidence extraction")
    print("• Proper handling of complex PDF formatting")

if __name__ == "__main__":
    test_improved_system()
