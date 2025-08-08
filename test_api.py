#!/usr/bin/env python3
"""
Simple test script for the HackRx API endpoint.
"""
import requests
import json
import time

def test_api():
    """Test the API endpoint."""
    
    # Test URL (update this to your deployed URL)
    base_url = "http://localhost:8000"  # Change to your Render URL when deployed
    
    # Test data
    test_data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?"
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer 66c272350145dbd2c98576a1ae3f62bacfcd74a73ceab1546744e495b65d67e4"
    }
    
    print("🧪 Testing HackRx API")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed!")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            for service, status in data.get('services', {}).items():
                print(f"   - {service}: {status}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    print("\n2. Testing main API endpoint...")
    print(f"   URL: {base_url}/api/v1/hackrx/run")
    print(f"   Questions: {len(test_data['questions'])}")
    
    # Test 2: Main API
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/v1/hackrx/run",
            headers=headers,
            json=test_data,
            timeout=300  # 5 minutes
        )
        end_time = time.time()
        
        print(f"   ⏱️  Request time: {end_time - start_time:.2f} seconds")
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API test successful!")
            print(f"   📄 Document URL: {result.get('document_url', 'N/A')}")
            print(f"   ❓ Questions Processed: {result.get('questions_processed', 'N/A')}")
            print(f"   ⏱️  Processing Time: {result.get('processing_time', 'N/A')} seconds")
            
            print("\n   📋 Answers:")
            for i, answer in enumerate(result.get('answers', []), 1):
                print(f"   {i}. {answer.get('question', 'N/A')[:50]}...")
                print(f"      Answer: {answer.get('answer', 'N/A')[:100]}...")
                print(f"      Confidence: {answer.get('confidence', 'N/A')}")
                print()
            
            # Save response to file
            with open('api_test_response.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print("   💾 Full response saved to: api_test_response.json")
            
        else:
            print(f"❌ API test failed!")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running")
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    test_api()
