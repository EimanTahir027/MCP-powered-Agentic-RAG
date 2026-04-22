"""
ChromaDB Tool for RAG System
Manages document storage, retrieval, and vector similarity search
"""

import os
import json
from typing import Optional, List, Dict, Any
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


class ChromaTool:
    """Vector search tool using ChromaDB for RAG retrieval"""
    
    def __init__(self, persist_dir: str = "./vector_store", collection_name: str = "documents"):
        """
        Initialize ChromaDB client and collection
        
        Args:
            persist_dir: Directory to persist vector store
            collection_name: Name of the collection to create
        """
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Use SentenceTransformer for embeddings
        self.embedding_func = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_func,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, documents: List[str], ids: Optional[List[str]] = None, 
                      metadata: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Add documents to the vector store
        
        Args:
            documents: List of document texts to add
            ids: Optional list of document IDs (auto-generated if not provided)
            metadata: Optional list of metadata dicts for each document
        """
        if not ids:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        if not metadata:
            metadata = [{"source": "unknown"} for _ in documents]
        
        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadata
        )
        print(f"Added {len(documents)} documents to collection")
    
    def search(self, query: str, n_results: int = 3) -> Dict[str, Any]:
        """
        Search for documents similar to the query
        
        Args:
            query: Search query string
            n_results: Number of results to return
            
        Returns:
            Dict containing documents, ids, distances, and metadata
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "ids": results["ids"][0] if results["ids"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else []
        }
    
    def search_formatted(self, query: str, n_results: int = 3) -> str:
        """
        Search and return formatted results as a string
        
        Args:
            query: Search query string
            n_results: Number of results to return
            
        Returns:
            Formatted string with retrieved documents
        """
        results = self.search(query, n_results)
        
        if not results["documents"]:
            return "No documents found matching the query."
        
        formatted = "Retrieved Documents:\n"
        formatted += "-" * 50 + "\n"
        
        for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"]), 1):
            formatted += f"\n[Document {i}]\n"
            formatted += f"Content: {doc[:500]}...\n" if len(doc) > 500 else f"Content: {doc}\n"
            if meta:
                formatted += f"Source: {meta.get('source', 'Unknown')}\n"
        
        return formatted
    
    def delete_collection(self) -> None:
        """Delete the current collection"""
        self.client.delete_collection(name=self.collection_name)
        print(f"Deleted collection: {self.collection_name}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the current collection"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_dir": self.persist_dir
        }


# Example usage and test functions
def load_sample_documents(tool: ChromaTool) -> None:
    """Load sample documents for testing"""
    sample_docs = [
        "Artificial Intelligence is revolutionizing many industries by enabling machines to learn from data and make intelligent decisions without explicit programming.",
        "The Model Context Protocol (MCP) enables modular tool use for AI agents by providing a standardized way to connect language models to external services.",
        "Vector databases like ChromaDB store embeddings of text, enabling fast semantic similarity search and retrieval of relevant documents.",
        "Retrieval-Augmented Generation (RAG) combines the benefits of retrieval and generation, allowing AI systems to ground their responses in factual, retrieved content.",
        "Ollama provides a simple way to run large language models locally, supporting models like Mistral, Llama, and others without requiring expensive cloud infrastructure."
    ]
    
    ids = [f"sample_doc_{i}" for i in range(len(sample_docs))]
    metadata = [{"source": "sample", "type": "general_info"} for _ in sample_docs]
    
    tool.add_documents(sample_docs, ids, metadata)


if __name__ == "__main__":
    # Test the ChromaTool
    tool = ChromaTool(persist_dir="./vector_store")
    
    # Load sample documents
    load_sample_documents(tool)
    
    # Test search
    query = "What is MCP?"
    results = tool.search_formatted(query)
    print(results)
    
    # Print stats
    stats = tool.get_collection_stats()
    print(f"\nCollection Stats: {json.dumps(stats, indent=2)}")
