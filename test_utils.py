"""
Test Utilities for MCP-Powered Agentic RAG
Useful functions for testing and validating the system
"""

import json
import time
from typing import Dict, Any, List
import requests


class SystemTester:
    """Test various components of the RAG system"""
    
    def __init__(self, api_url: str = "http://localhost:8000", ollama_url: str = "http://localhost:11434"):
        self.api_url = api_url
        self.ollama_url = ollama_url
        self.results = {}
    
    def test_ollama_connection(self) -> Dict[str, Any]:
        """Test connection to Ollama server"""
        print("Testing Ollama connection...")
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            models = response.json().get("models", [])
            
            result = {
                "status": "✅ PASS" if models else "⚠️ WARNING",
                "message": f"Found {len(models)} model(s)",
                "models": [m.get("name") for m in models]
            }
        except Exception as e:
            result = {
                "status": "❌ FAIL",
                "message": str(e)
            }
        
        self.results["ollama_connection"] = result
        print(f"  {result['status']}: {result['message']}")
        return result
    
    def test_api_health(self) -> Dict[str, Any]:
        """Test API health endpoint"""
        print("Testing API health...")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            data = response.json()
            
            result = {
                "status": "✅ PASS" if data.get("status") == "healthy" else "⚠️ WARNING",
                "message": f"API healthy, {data.get('vector_store_documents', 0)} documents"
            }
        except Exception as e:
            result = {
                "status": "❌ FAIL",
                "message": str(e)
            }
        
        self.results["api_health"] = result
        print(f"  {result['status']}: {result['message']}")
        return result
    
    def test_query_performance(self) -> Dict[str, Any]:
        """Test query performance"""
        print("Testing query performance...")
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/query",
                json={
                    "query": "What is AI?",
                    "use_context": True,
                    "n_results": 3
                },
                timeout=60
            )
            elapsed = time.time() - start_time
            
            data = response.json()
            result = {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "response_time": f"{elapsed:.2f}s",
                "status_code": response.status_code,
                "has_response": bool(data.get("response"))
            }
        except Exception as e:
            result = {
                "status": "❌ FAIL",
                "message": str(e)
            }
        
        self.results["query_performance"] = result
        print(f"  {result['status']}: {result.get('response_time', 'N/A')}")
        return result
    
    def test_document_operations(self) -> Dict[str, Any]:
        """Test document add/search operations"""
        print("Testing document operations...")
        try:
            # Add test document
            add_response = requests.post(
                f"{self.api_url}/documents",
                json={
                    "documents": ["Test document for validation"],
                    "ids": ["test_doc"],
                    "metadata": [{"source": "test"}]
                },
                timeout=10
            )
            
            add_success = add_response.status_code == 200
            
            # Search for it
            search_response = requests.post(
                f"{self.api_url}/search",
                json={
                    "query": "test document",
                    "n_results": 1
                },
                timeout=10
            )
            
            search_success = search_response.status_code == 200
            
            result = {
                "status": "✅ PASS" if (add_success and search_success) else "❌ FAIL",
                "add_success": add_success,
                "search_success": search_success
            }
        except Exception as e:
            result = {
                "status": "❌ FAIL",
                "message": str(e)
            }
        
        self.results["document_operations"] = result
        print(f"  {result['status']}")
        return result
    
    def test_vector_store(self) -> Dict[str, Any]:
        """Test vector store functionality"""
        print("Testing vector store...")
        try:
            from tools.chromadb_tool import ChromaTool
            
            tool = ChromaTool(persist_dir="./vector_store")
            stats = tool.get_collection_stats()
            
            result = {
                "status": "✅ PASS",
                "collection": stats.get("collection_name"),
                "documents": stats.get("document_count"),
                "location": stats.get("persist_dir")
            }
        except Exception as e:
            result = {
                "status": "❌ FAIL",
                "message": str(e)
            }
        
        self.results["vector_store"] = result
        print(f"  {result['status']}: {result.get('documents', 0)} documents")
        return result
    
    def run_all_tests(self) -> Dict[str, Dict[str, Any]]:
        """Run all tests"""
        print("\n" + "="*50)
        print("🧪 Running System Tests")
        print("="*50 + "\n")
        
        self.test_ollama_connection()
        self.test_api_health()
        self.test_vector_store()
        self.test_document_operations()
        self.test_query_performance()
        
        print("\n" + "="*50)
        print("📊 Test Summary")
        print("="*50)
        
        passed = sum(1 for r in self.results.values() if "✅" in str(r.get("status", "")))
        total = len(self.results)
        
        print(f"\nPassed: {passed}/{total}")
        print(f"Failed: {total - passed}/{total}\n")
        
        for test_name, result in self.results.items():
            print(f"{result['status']}: {test_name}")
        
        return self.results


class PerformanceBenchmark:
    """Benchmark system performance"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.results = []
    
    def benchmark_query_latency(self, num_queries: int = 10) -> Dict[str, float]:
        """Benchmark query latency"""
        print(f"\n🔄 Benchmarking query latency ({num_queries} queries)...")
        
        times = []
        for i in range(num_queries):
            try:
                start = time.time()
                requests.post(
                    f"{self.api_url}/query",
                    json={
                        "query": f"Test query number {i}",
                        "use_context": True,
                        "n_results": 3
                    },
                    timeout=60
                )
                times.append(time.time() - start)
                print(f"  Query {i+1}: {times[-1]:.2f}s")
            except Exception as e:
                print(f"  Query {i+1}: Error - {str(e)}")
        
        if times:
            results = {
                "min": min(times),
                "max": max(times),
                "avg": sum(times) / len(times),
                "total": sum(times),
                "samples": len(times)
            }
            
            print(f"\n📊 Latency Statistics:")
            print(f"  Average: {results['avg']:.2f}s")
            print(f"  Min: {results['min']:.2f}s")
            print(f"  Max: {results['max']:.2f}s")
            print(f"  Total: {results['total']:.2f}s")
            
            return results
        
        return {}
    
    def benchmark_document_operations(self) -> Dict[str, Any]:
        """Benchmark document operations"""
        print("\n📚 Benchmarking document operations...")
        
        # Add documents
        docs = [f"Test document {i}" for i in range(100)]
        
        start = time.time()
        response = requests.post(
            f"{self.api_url}/documents",
            json={"documents": docs},
            timeout=30
        )
        add_time = time.time() - start
        
        print(f"  Add 100 docs: {add_time:.2f}s")
        
        return {"add_time": add_time, "documents": len(docs)}


def generate_test_report(results: Dict[str, Dict[str, Any]]) -> str:
    """Generate a test report"""
    report = """
╔════════════════════════════════════════════════════════════════╗
║         MCP-Powered Agentic RAG - Test Report                 ║
╚════════════════════════════════════════════════════════════════╝

TEST RESULTS:
"""
    
    for test_name, result in results.items():
        status = result.get("status", "N/A")
        report += f"\n{test_name.upper()}: {status}\n"
        
        for key, value in result.items():
            if key != "status":
                report += f"  - {key}: {value}\n"
    
    return report


if __name__ == "__main__":
    import sys
    
    # Run tests
    tester = SystemTester()
    results = tester.run_all_tests()
    
    # Optional: Run benchmarks
    if len(sys.argv) > 1 and sys.argv[1] == "--benchmark":
        benchmark = PerformanceBenchmark()
        benchmark.benchmark_query_latency(num_queries=5)
        benchmark.benchmark_document_operations()
    
    # Generate report
    report = generate_test_report(results)
    print(report)
