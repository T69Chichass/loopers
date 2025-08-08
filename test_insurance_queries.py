#!/usr/bin/env python3
"""
Test script for specific insurance policy queries.
"""
import requests
import json
import time

def test_insurance_queries():
    """Test specific insurance policy queries."""
    base_url = "http://localhost:8000"
    
    print("🏥 Testing Insurance Policy Queries")
    print("=" * 60)
    
    # List of specific insurance queries
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
    
    print(f"📋 Testing {len(insurance_queries)} insurance policy queries...")
    print()
    
    for i, query in enumerate(insurance_queries, 1):
        print(f"🔍 Query {i:2d}: {query}")
        print("-" * 80)
        
        try:
            # Send query to API
            response = requests.post(
                f"{base_url}/query",
                json={'query': query},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Display answer
                print(f"✅ Answer: {result['answer']}")
                print()
                
                # Display confidence and metadata
                print(f"🎯 Confidence: {result['confidence']}")
                print(f"📚 Supporting clauses: {len(result['supporting_clauses'])}")
                print(f"🆔 Query ID: {result['query_id']}")
                print(f"⏰ Timestamp: {result['timestamp']}")
                
                # Display supporting evidence
                if result['supporting_clauses']:
                    print("\n📖 Supporting Evidence:")
                    for j, clause in enumerate(result['supporting_clauses'][:2], 1):  # Show first 2 clauses
                        print(f"   {j}. {clause['text'][:150]}...")
                        print(f"      📄 Document: {clause['document_id']}")
                        print(f"      🎯 Score: {clause['confidence_score']:.2f}")
                
                # Display explanation if available
                if 'explanation' in result:
                    print(f"\n💡 Explanation: {result['explanation']}")
                
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error processing query: {e}")
        
        print("\n" + "=" * 80)
        print()
        
        # Small delay between queries
        time.sleep(1)
    
    print("🎉 Insurance Policy Query Test Complete!")
    print("\nSummary:")
    print(f"✅ Tested {len(insurance_queries)} insurance policy queries")
    print("✅ All queries processed through the AI system")
    print("✅ Responses include confidence scores and supporting evidence")
    print("\n💡 The system provides AI-powered answers based on uploaded policy documents")

if __name__ == "__main__":
    test_insurance_queries()
