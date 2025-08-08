#!/usr/bin/env python3
"""
Process policy queries with document download and upload.
"""
import requests
import json
import time
import tempfile
from pathlib import Path

def download_and_process_policy():
    """Download PDF from URL, upload it, and process queries."""
    base_url = "http://localhost:8000"
    
    print("📥 Processing Policy Document and Queries")
    print("=" * 60)
    
    # Document URL and questions
    document_url = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
    
    questions = [
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
    
    # Step 1: Download the PDF
    print("1️⃣ Downloading policy document...")
    try:
        response = requests.get(document_url, timeout=30)
        if response.status_code == 200:
            print("✅ Document downloaded successfully")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(response.content)
                tmp_path = Path(tmp_file.name)
            
            print(f"📄 Saved to: {tmp_path}")
            
        else:
            print(f"❌ Failed to download document: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error downloading document: {e}")
        return
    
    # Step 2: Upload the document
    print("\n2️⃣ Uploading document to API...")
    try:
        with open(tmp_path, 'rb') as pdf_file:
            files = {
                'file': ('policy.pdf', pdf_file, 'application/pdf')
            }
            
            data = {
                'document_type': 'insurance',
                'category': 'health_insurance',
                'title': 'National Parivar Mediclaim Plus Policy'
            }
            
            upload_response = requests.post(
                f"{base_url}/documents/upload",
                files=files,
                data=data
            )
            
            if upload_response.status_code == 200:
                upload_result = upload_response.json()
                print("✅ Document uploaded successfully!")
                print(f"   📄 Document ID: {upload_result['document_id']}")
                print(f"   📝 Title: {upload_result['title']}")
                print(f"   📊 Text Length: {upload_result['text_length']} characters")
                print(f"   🧩 Chunks Created: {upload_result['chunk_count']}")
                print(f"   ⏱️ Processing Time: {upload_result['processing_time']:.3f}s")
                
                document_id = upload_result['document_id']
                
            else:
                print(f"❌ Upload failed: {upload_response.status_code}")
                print(f"Error: {upload_response.text}")
                return
                
    except Exception as e:
        print(f"❌ Error uploading document: {e}")
        return
    
    finally:
        # Clean up temporary file
        tmp_path.unlink(missing_ok=True)
    
    # Step 3: Process all questions
    print(f"\n3️⃣ Processing {len(questions)} questions...")
    
    results = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n🔍 Question {i:2d}: {question}")
        print("-" * 80)
        
        try:
            # Send query to API
            query_response = requests.post(
                f"{base_url}/query",
                json={'query': question},
                timeout=30
            )
            
            if query_response.status_code == 200:
                result = query_response.json()
                
                # Display answer
                print(f"✅ Answer: {result['answer']}")
                print(f"🎯 Confidence: {result['confidence']}")
                print(f"📚 Supporting clauses: {len(result['supporting_clauses'])}")
                
                # Store result
                results.append({
                    'question': question,
                    'answer': result['answer'],
                    'confidence': result['confidence'],
                    'supporting_clauses_count': len(result['supporting_clauses']),
                    'query_id': result['query_id'],
                    'timestamp': result['timestamp']
                })
                
            else:
                print(f"❌ Query failed: {query_response.status_code}")
                print(f"Error: {query_response.text}")
                
        except Exception as e:
            print(f"❌ Error processing query: {e}")
        
        print("=" * 80)
        
        # Small delay between queries
        time.sleep(1)
    
    # Step 4: Save results to file
    print(f"\n4️⃣ Saving results...")
    try:
        output_data = {
            'document_id': document_id,
            'document_title': 'National Parivar Mediclaim Plus Policy',
            'total_questions': len(questions),
            'processed_questions': len(results),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': results
        }
        
        with open('policy_query_results.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Results saved to 'policy_query_results.json'")
        
    except Exception as e:
        print(f"❌ Error saving results: {e}")
    
    print("\n🎉 Policy Query Processing Complete!")
    print(f"\nSummary:")
    print(f"✅ Document downloaded and uploaded")
    print(f"✅ {len(results)}/{len(questions)} questions processed")
    print(f"✅ Results saved to file")
    print(f"\n📄 Document ID: {document_id}")
    print(f"📊 Average confidence: {sum(r['confidence'] == 'high' for r in results)}/{len(results)} high confidence")

if __name__ == "__main__":
    download_and_process_policy()
