#!/usr/bin/env python3
"""
Example: Process Insurance Policy Document
This script demonstrates how to use the PolicyProcessor to handle
insurance policy documents and queries.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from policy_processor import PolicyProcessor


def main():
    """Example usage of PolicyProcessor."""
    
    # Insurance policy questions
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
    
    # Document URL (replace with your actual URL)
    document_url = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
    
    # Initialize processor
    processor = PolicyProcessor(base_url="http://localhost:8000")
    
    # Process the policy document
    success = processor.process_policy_document(
        document_url=document_url,
        questions=questions,
        title="National Parivar Mediclaim Plus Policy"
    )
    
    if success:
        print("\n✅ Policy processing completed successfully!")
        print("📄 Check 'policy_query_results.json' for detailed results.")
    else:
        print("\n❌ Policy processing failed!")
        print("🔍 Check the logs for error details.")


if __name__ == "__main__":
    main()
