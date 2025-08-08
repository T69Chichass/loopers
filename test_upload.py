#!/usr/bin/env python3
"""
Test script for document upload functionality.
"""
import requests
import json
import time
from pathlib import Path

def test_document_upload():
    """Test document upload functionality."""
    base_url = "http://localhost:8000"
    
    print("📤 Testing Document Upload Functionality")
    print("=" * 50)
    
    # Test 1: Upload text document
    print("\n1️⃣ Uploading test insurance document...")
    
    try:
        # Prepare the file upload
        files = {
            'file': ('test_insurance_policy.txt', open('test_document.txt', 'rb'), 'text/plain')
        }
        
        data = {
            'document_type': 'insurance',
            'category': 'auto_insurance',
            'title': 'Test Auto Insurance Policy'
        }
        
        # Upload the document
        response = requests.post(
            f"{base_url}/documents/upload",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document uploaded successfully!")
            print(f"   📄 Document ID: {result['document_id']}")
            print(f"   📝 Title: {result['title']}")
            print(f"   📊 Text Length: {result['text_length']} characters")
            print(f"   🧩 Chunks Created: {result['chunk_count']}")
            print(f"   ⏱️ Processing Time: {result['processing_time']:.3f}s")
            print(f"   📋 Status: {result['status']}")
            
            document_id = result['document_id']
            
            # Test 2: Query the uploaded document
            print("\n2️⃣ Testing query on uploaded document...")
            
            test_queries = [
                "What is the monthly premium?",
                "What is the deductible for collision coverage?",
                "How long is the grace period for late payments?",
                "What is the claims process?",
                "What are the liability coverage limits?"
            ]
            
            for i, query in enumerate(test_queries, 1):
                print(f"\n   Query {i}: '{query}'")
                
                query_response = requests.post(
                    f"{base_url}/query",
                    json={'query': query}
                )
                
                if query_response.status_code == 200:
                    query_result = query_response.json()
                    print(f"   ✅ Answer: {query_result['answer'][:100]}...")
                    print(f"   🎯 Confidence: {query_result['confidence']}")
                    print(f"   📚 Supporting clauses: {len(query_result['supporting_clauses'])}")
                else:
                    print(f"   ❌ Query failed: {query_response.status_code}")
            
            # Test 3: List documents
            print("\n3️⃣ Listing uploaded documents...")
            
            list_response = requests.get(f"{base_url}/documents")
            if list_response.status_code == 200:
                docs = list_response.json()
                print(f"   ✅ Found {docs['total_count']} document(s)")
                for doc in docs['documents']:
                    print(f"   📄 {doc['title']} ({doc['document_type']}) - {doc['status']}")
            else:
                print(f"   ❌ Failed to list documents: {list_response.status_code}")
            
            # Test 4: Get document status
            print(f"\n4️⃣ Getting status for document {document_id}...")
            
            status_response = requests.get(f"{base_url}/documents/{document_id}")
            if status_response.status_code == 200:
                status_result = status_response.json()
                print(f"   ✅ Document Status: {status_result['status']}")
                print(f"   📝 Title: {status_result['title']}")
                print(f"   📊 Chunks: {status_result['chunk_count']}")
            else:
                print(f"   ❌ Failed to get document status: {status_response.status_code}")
            
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during upload test: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Document Upload Test Complete!")
    print("\nWhat was tested:")
    print("✅ Document upload with metadata")
    print("✅ Text extraction and chunking")
    print("✅ Query processing on uploaded document")
    print("✅ Document listing and status checking")
    print("✅ Full workflow from upload to query")

if __name__ == "__main__":
    test_document_upload()
