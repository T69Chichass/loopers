"""
Test script for the LLM-Powered Intelligent Query-Retrieval System API.
This script tests the main endpoints and functionality.
"""
import asyncio
import json
import time
from typing import Dict, Any
import httpx
import pytest
from unittest.mock import Mock, patch

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30

class APITester:
    """Test runner for the API endpoints."""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
    
    async def test_health_endpoint(self) -> Dict[str, Any]:
        """Test the health check endpoint."""
        print("🔍 Testing health endpoint...")
        
        try:
            response = await self.client.get(f"{self.base_url}/health")
            result = {
                "endpoint": "/health",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "content": response.json() if response.status_code == 200 else response.text
            }
            
            if result["success"]:
                print("✅ Health endpoint working correctly")
                services = result["content"].get("services", {})
                for service, status in services.items():
                    status_emoji = "✅" if status == "healthy" else "❌"
                    print(f"   {status_emoji} {service}: {status}")
            else:
                print(f"❌ Health endpoint failed: {result['status_code']}")
                
            return result
            
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            return {
                "endpoint": "/health",
                "success": False,
                "error": str(e)
            }
    
    async def test_root_endpoint(self) -> Dict[str, Any]:
        """Test the root endpoint."""
        print("\n🔍 Testing root endpoint...")
        
        try:
            response = await self.client.get(f"{self.base_url}/")
            result = {
                "endpoint": "/",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "content": response.json() if response.status_code == 200 else response.text
            }
            
            if result["success"]:
                print("✅ Root endpoint working correctly")
                print(f"   API Name: {result['content'].get('name', 'Unknown')}")
                print(f"   Version: {result['content'].get('version', 'Unknown')}")
            else:
                print(f"❌ Root endpoint failed: {result['status_code']}")
                
            return result
            
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
            return {
                "endpoint": "/",
                "success": False,
                "error": str(e)
            }
    
    async def test_query_endpoint_validation(self) -> Dict[str, Any]:
        """Test query endpoint input validation."""
        print("\n🔍 Testing query endpoint validation...")
        
        test_cases = [
            {
                "name": "Empty query",
                "payload": {"query": ""},
                "expected_status": 422
            },
            {
                "name": "Whitespace only query",
                "payload": {"query": "   "},
                "expected_status": 422
            },
            {
                "name": "Missing query field",
                "payload": {},
                "expected_status": 422
            },
            {
                "name": "Very long query",
                "payload": {"query": "a" * 1001},
                "expected_status": 422
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            try:
                response = await self.client.post(
                    f"{self.base_url}/query",
                    json=test_case["payload"],
                    headers={"Content-Type": "application/json"}
                )
                
                success = response.status_code == test_case["expected_status"]
                status_emoji = "✅" if success else "❌"
                
                print(f"   {status_emoji} {test_case['name']}: {response.status_code} (expected {test_case['expected_status']})")
                
                results.append({
                    "test_name": test_case["name"],
                    "success": success,
                    "status_code": response.status_code,
                    "expected_status": test_case["expected_status"]
                })
                
            except Exception as e:
                print(f"   ❌ {test_case['name']}: Error - {e}")
                results.append({
                    "test_name": test_case["name"],
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "endpoint": "/query (validation)",
            "results": results,
            "overall_success": all(r.get("success", False) for r in results)
        }
    
    async def test_query_endpoint_functionality(self) -> Dict[str, Any]:
        """Test query endpoint with valid input (mocked services)."""
        print("\n🔍 Testing query endpoint functionality...")
        
        test_queries = [
            "What is covered under this insurance policy?",
            "Are dental procedures included in the coverage?",
            "What are the requirements for filing a claim?",
            "Does this policy cover emergency room visits?",
            "What is the maximum coverage amount?"
        ]
        
        results = []
        
        for query in test_queries:
            try:
                start_time = time.time()
                response = await self.client.post(
                    f"{self.base_url}/query",
                    json={"query": query},
                    headers={"Content-Type": "application/json"}
                )
                response_time = time.time() - start_time
                
                result = {
                    "query": query,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "success": response.status_code == 200
                }
                
                if response.status_code == 200:
                    try:
                        content = response.json()
                        result["content"] = content
                        result["has_answer"] = bool(content.get("answer"))
                        result["has_supporting_clauses"] = bool(content.get("supporting_clauses"))
                        result["has_explanation"] = bool(content.get("explanation"))
                        result["query_id"] = content.get("query_id")
                        
                        status_emoji = "✅"
                        print(f"   {status_emoji} Query processed successfully ({response_time:.2f}s)")
                        print(f"      Answer length: {len(content.get('answer', ''))}")
                        print(f"      Supporting clauses: {len(content.get('supporting_clauses', []))}")
                        print(f"      Confidence: {content.get('confidence', 'unknown')}")
                        
                    except json.JSONDecodeError as e:
                        result["json_error"] = str(e)
                        print(f"   ❌ JSON parsing error: {e}")
                        
                else:
                    print(f"   ❌ Query failed: {response.status_code}")
                    try:
                        error_content = response.json()
                        result["error_content"] = error_content
                        print(f"      Error: {error_content.get('message', 'Unknown error')}")
                    except:
                        result["error_text"] = response.text
                
                results.append(result)
                
            except Exception as e:
                print(f"   ❌ Query error: {e}")
                results.append({
                    "query": query,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "endpoint": "/query (functionality)",
            "results": results,
            "total_queries": len(test_queries),
            "successful_queries": sum(1 for r in results if r.get("success", False)),
            "average_response_time": sum(r.get("response_time", 0) for r in results) / len(results) if results else 0
        }
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling scenarios."""
        print("\n🔍 Testing error handling...")
        
        test_cases = [
            {
                "name": "Invalid JSON",
                "payload": "invalid json",
                "headers": {"Content-Type": "application/json"}
            },
            {
                "name": "Wrong content type",
                "payload": {"query": "test"},
                "headers": {"Content-Type": "text/plain"}
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            try:
                if isinstance(test_case["payload"], str):
                    # Send raw string for invalid JSON test
                    response = await self.client.post(
                        f"{self.base_url}/query",
                        content=test_case["payload"],
                        headers=test_case["headers"]
                    )
                else:
                    response = await self.client.post(
                        f"{self.base_url}/query",
                        json=test_case["payload"],
                        headers=test_case["headers"]
                    )
                
                # Error handling should return 4xx status codes
                success = 400 <= response.status_code < 500
                status_emoji = "✅" if success else "❌"
                
                print(f"   {status_emoji} {test_case['name']}: {response.status_code}")
                
                results.append({
                    "test_name": test_case["name"],
                    "success": success,
                    "status_code": response.status_code
                })
                
            except Exception as e:
                print(f"   ❌ {test_case['name']}: Error - {e}")
                results.append({
                    "test_name": test_case["name"],
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "endpoint": "/query (error handling)",
            "results": results,
            "overall_success": all(r.get("success", False) for r in results)
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all API tests."""
        print("🚀 Starting API tests...\n")
        start_time = time.time()
        
        test_results = {}
        
        # Test health endpoint
        test_results["health"] = await self.test_health_endpoint()
        
        # Test root endpoint
        test_results["root"] = await self.test_root_endpoint()
        
        # Test query validation
        test_results["query_validation"] = await self.test_query_endpoint_validation()
        
        # Test query functionality (may fail if services not configured)
        test_results["query_functionality"] = await self.test_query_endpoint_functionality()
        
        # Test error handling
        test_results["error_handling"] = await self.test_error_handling()
        
        total_time = time.time() - start_time
        
        # Summary
        print(f"\n📊 Test Summary (Total time: {total_time:.2f}s)")
        print("=" * 50)
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, result in test_results.items():
            if isinstance(result.get("success"), bool):
                total_tests += 1
                if result["success"]:
                    passed_tests += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            elif "results" in result:
                sub_total = len(result["results"])
                sub_passed = sum(1 for r in result["results"] if r.get("success", False))
                total_tests += sub_total
                passed_tests += sub_passed
                print(f"{'✅' if sub_passed == sub_total else '⚠️'} {test_name}: {sub_passed}/{sub_total} passed")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        
        await self.client.aclose()
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "total_time": total_time,
            "detailed_results": test_results
        }


# Standalone test functions for pytest compatibility
@pytest.mark.asyncio
async def test_health_endpoint():
    """Pytest compatible health endpoint test."""
    tester = APITester()
    result = await tester.test_health_endpoint()
    await tester.client.aclose()
    assert result["success"], f"Health endpoint failed: {result}"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Pytest compatible root endpoint test."""
    tester = APITester()
    result = await tester.test_root_endpoint()
    await tester.client.aclose()
    assert result["success"], f"Root endpoint failed: {result}"


@pytest.mark.asyncio
async def test_query_validation():
    """Pytest compatible query validation test."""
    tester = APITester()
    result = await tester.test_query_endpoint_validation()
    await tester.client.aclose()
    assert result["overall_success"], f"Query validation failed: {result}"


# Main execution
async def main():
    """Main test execution function."""
    tester = APITester()
    results = await tester.run_all_tests()
    return results


if __name__ == "__main__":
    print("🧪 LLM Query-Retrieval System API Tests")
    print("=" * 50)
    print("Make sure the API server is running on http://localhost:8000")
    print("Start with: python main.py or uvicorn main:app --reload")
    print()
    
    try:
        results = asyncio.run(main())
        
        # Exit with appropriate code
        if results["success_rate"] == 1.0:
            print("\n🎉 All tests passed!")
            exit(0)
        elif results["success_rate"] > 0.5:
            print(f"\n⚠️ Some tests failed (success rate: {results['success_rate']:.1%})")
            exit(1)
        else:
            print(f"\n💥 Many tests failed (success rate: {results['success_rate']:.1%})")
            exit(2)
            
    except KeyboardInterrupt:
        print("\n\n⛔ Tests interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        exit(1)
