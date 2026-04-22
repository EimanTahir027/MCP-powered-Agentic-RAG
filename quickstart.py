#!/usr/bin/env python3
"""
Quick Start Script for MCP-Powered Agentic RAG
Demonstrates different ways to use the system
"""

import sys
import os
from pathlib import Path


def check_dependencies():
    """Check if all required packages are installed"""
    print("🔍 Checking dependencies...")
    required_packages = [
        'chromadb', 'sentence_transformers', 'requests', 
        'fastapi', 'uvicorn', 'langchain', 'ollama'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"Install them with: pip install {' '.join(missing)}")
        return False
    
    print("✅ All dependencies installed!\n")
    return True


def check_ollama():
    """Check if Ollama server is running"""
    print("🔍 Checking Ollama connection...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        data = response.json()
        
        if data.get("models"):
            print(f"✅ Ollama running with {len(data['models'])} model(s)")
            print(f"   Models: {', '.join([m.get('name', 'unknown') for m in data['models'][:3]])}")
            return True
        else:
            print("❌ Ollama running but no models found")
            print("   Run: ollama pull mistral")
            return False
    except Exception as e:
        print(f"❌ Ollama not responding: {str(e)}")
        print("   Start Ollama with: ollama serve")
        return False


def show_menu():
    """Display main menu"""
    print("\n" + "="*50)
    print("🤖 MCP-Powered Agentic RAG - Quick Start")
    print("="*50)
    print("\nChoose an option:")
    print("1. 💬 Start Interactive Chat")
    print("2. 🌐 Start FastAPI Server")
    print("3. 🎨 Start Streamlit Frontend")
    print("4. 🧪 Test Vector Store")
    print("5. 📚 Load Sample Documents")
    print("6. ℹ️  Show System Info")
    print("0. ❌ Exit")
    print("-"*50)


def start_chat():
    """Start interactive chat"""
    print("\n🚀 Starting Chat Interface...")
    print("Make sure Ollama is running!")
    os.system("python rag_agent.py")


def start_server():
    """Start FastAPI server"""
    print("\n🚀 Starting FastAPI MCP Server...")
    print("Server will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop\n")
    os.system("python main.py")


def start_streamlit():
    """Start Streamlit frontend"""
    print("\n🚀 Starting Streamlit Frontend...")
    print("Frontend will be available at: http://localhost:8501")
    print("Make sure the FastAPI server is running!")
    os.system("streamlit run streamlit_app.py")


def test_vector_store():
    """Test vector store functionality"""
    print("\n🧪 Testing Vector Store...")
    try:
        from tools.chromadb_tool import ChromaTool, load_sample_documents
        
        tool = ChromaTool(persist_dir="./vector_store")
        
        # Check if documents exist
        stats = tool.get_collection_stats()
        if stats["document_count"] == 0:
            print("Loading sample documents...")
            load_sample_documents(tool)
        
        # Print stats
        print(f"✅ Collection: {stats['collection_name']}")
        print(f"✅ Documents: {stats['document_count']}")
        print(f"✅ Storage: {stats['persist_dir']}")
        
        # Test search
        print("\n🔍 Testing search...")
        results = tool.search("What is AI?", n_results=2)
        print(f"✅ Search returned {len(results['documents'])} documents")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def load_documents():
    """Load sample documents"""
    print("\n📚 Loading Sample Documents...")
    try:
        from tools.chromadb_tool import ChromaTool, load_sample_documents
        
        tool = ChromaTool(persist_dir="./vector_store")
        load_sample_documents(tool)
        
        stats = tool.get_collection_stats()
        print(f"✅ Loaded! Total documents: {stats['document_count']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def show_info():
    """Show system information"""
    print("\n" + "="*50)
    print("ℹ️  System Information")
    print("="*50)
    
    # Python version
    print(f"\n📌 Python Version: {sys.version}")
    
    # Project structure
    print("\n📁 Project Structure:")
    project_files = [
        "main.py",
        "rag_agent.py",
        "mcp_config.yaml",
        "requirements.txt",
        "streamlit_app.py",
        "tools/chromadb_tool.py",
        "README.md"
    ]
    
    for file in project_files:
        exists = "✅" if Path(file).exists() else "❌"
        print(f"  {exists} {file}")
    
    # API endpoints
    print("\n🌐 API Endpoints (when server running):")
    endpoints = [
        ("GET", "/", "API info"),
        ("GET", "/health", "Health check"),
        ("POST", "/query", "Query agent"),
        ("POST", "/search", "Search documents"),
        ("POST", "/documents", "Add documents"),
        ("GET", "/stats", "System stats"),
    ]
    
    for method, path, desc in endpoints:
        print(f"  {method:6} {path:20} - {desc}")


def main():
    """Main function"""
    # Check dependencies
    if not check_dependencies():
        print("Please install missing dependencies first.")
        sys.exit(1)
    
    # Check Ollama
    ollama_ready = check_ollama()
    
    while True:
        show_menu()
        
        choice = input("Enter choice (0-6): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye!")
            sys.exit(0)
        elif choice == "1":
            if ollama_ready:
                start_chat()
            else:
                print("❌ Ollama must be running to use chat!")
        elif choice == "2":
            start_server()
        elif choice == "3":
            start_streamlit()
        elif choice == "4":
            test_vector_store()
        elif choice == "5":
            load_documents()
        elif choice == "6":
            show_info()
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
        sys.exit(0)
