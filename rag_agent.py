"""
RAG Agent Module
Handles agent query logic, LLM interactions, and response generation
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from tools.chromadb_tool import ChromaTool


class RAGAgent:
    """Agentic RAG system with LLM reasoning"""
    
    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "mistral",
        vector_store_path: str = "./vector_store",
        max_tokens: int = 1024,
        temperature: float = 0.7
    ):
        """
        Initialize the RAG Agent
        
        Args:
            ollama_url: URL of the Ollama server
            model: Model name (e.g., 'mistral', 'llama3')
            vector_store_path: Path to the vector store
            max_tokens: Maximum tokens for LLM response
            temperature: Temperature for LLM sampling
        """
        self.ollama_url = ollama_url
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize vector store tool
        self.vector_store = ChromaTool(persist_dir=vector_store_path)
    
    def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama LLM with a prompt
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Generated response from the LLM
        """
        try:
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
            
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
        
        except requests.exceptions.ConnectionError:
            return "Error: Unable to connect to Ollama server. Make sure it's running."
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"
    
    def retrieve_context(self, query: str, n_results: int = 3) -> str:
        """
        Retrieve relevant context from vector store
        
        Args:
            query: Search query
            n_results: Number of documents to retrieve
            
        Returns:
            Formatted context string
        """
        return self.vector_store.search_formatted(query, n_results)
    
    def build_prompt(self, query: str, context: str) -> str:
        """
        Build the final prompt with context injection
        
        Args:
            query: User query
            context: Retrieved context
            
        Returns:
            Final prompt for the LLM
        """
        prompt = f"""You are a helpful AI assistant. Use the provided context to answer the user's question accurately and concisely.

Context Information:
{context}

User Question: {query}

Please provide a clear and informative answer based on the context provided. If the context doesn't contain relevant information, say so and provide your best response based on your knowledge."""
        
        return prompt
    
    def get_response(self, query: str, use_context: bool = True, n_results: int = 3) -> Dict[str, Any]:
        """
        Get a response for a user query using RAG
        
        Args:
            query: User query
            use_context: Whether to use retrieved context
            n_results: Number of context documents to retrieve
            
        Returns:
            Dict containing the response and metadata
        """
        context = ""
        retrieved_docs = []
        
        if use_context:
            search_results = self.vector_store.search(query, n_results)
            retrieved_docs = search_results["documents"]
            context = self.vector_store.search_formatted(query, n_results)
        
        # Build and send prompt to LLM
        prompt = self.build_prompt(query, context) if use_context else query
        response = self._call_ollama(prompt)
        
        return {
            "query": query,
            "response": response,
            "retrieved_documents": retrieved_docs,
            "context_used": use_context,
            "model": self.model
        }
    
    def chat_loop(self) -> None:
        """Run an interactive chat loop"""
        print("=" * 60)
        print("MCP-Powered Agentic RAG System")
        print("=" * 60)
        print("Type 'quit' or 'exit' to stop")
        print("Type 'reload' to reload documents")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit']:
                    print("Exiting chat. Goodbye!")
                    break
                
                if user_input.lower() == 'reload':
                    from tools.chromadb_tool import load_sample_documents
                    load_sample_documents(self.vector_store)
                    print("Sample documents reloaded.")
                    continue
                
                # Get response
                result = self.get_response(user_input)
                
                print(f"\nAgent: {result['response']}")
                
                if result['retrieved_documents']:
                    print(f"\n[Used {len(result['retrieved_documents'])} retrieved documents as context]")
            
            except KeyboardInterrupt:
                print("\n\nExiting chat. Goodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")


def get_rag_response(query: str, ollama_url: str = "http://localhost:11434") -> Dict[str, Any]:
    """
    Standalone function to get RAG response
    
    Args:
        query: User query
        ollama_url: Ollama server URL
        
    Returns:
        Response dictionary
    """
    agent = RAGAgent(ollama_url=ollama_url)
    return agent.get_response(query)


if __name__ == "__main__":
    # Initialize agent
    agent = RAGAgent()
    
    # Load sample documents if vector store is empty
    if agent.vector_store.get_collection_stats()["document_count"] == 0:
        print("Loading sample documents...")
        from tools.chromadb_tool import load_sample_documents
        load_sample_documents(agent.vector_store)
    
    # Start chat loop
    agent.chat_loop()
