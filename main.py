"""
MCP Server for Agentic RAG System
Exposes RAG agent functionality via HTTP API with tool registration
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from tools.chromadb_tool import ChromaTool, load_sample_documents
from rag_agent import RAGAgent


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MCP-Powered Agentic RAG",
    description="Local agentic RAG system using Model Context Protocol",
    version="1.0.0"
)

# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    use_context: bool = True
    n_results: int = 3


class QueryResponse(BaseModel):
    query: str
    response: str
    retrieved_documents: list
    context_used: bool
    model: str


class DocumentsRequest(BaseModel):
    documents: list
    ids: Optional[list] = None
    metadata: Optional[list] = None


class SearchRequest(BaseModel):
    query: str
    n_results: int = 3


# Global agent and vector store instances
agent: Optional[RAGAgent] = None
vector_store: Optional[ChromaTool] = None


@app.on_event("startup")
async def startup_event():
    """Initialize agent and vector store on startup"""
    global agent, vector_store
    
    logger.info("Initializing RAG Agent and Vector Store...")
    
    vector_store = ChromaTool(persist_dir="./vector_store")
    agent = RAGAgent(vector_store_path="./vector_store")
    
    # Load sample documents if collection is empty
    if vector_store.get_collection_stats()["document_count"] == 0:
        logger.info("Loading sample documents...")
        load_sample_documents(vector_store)
    
    logger.info("RAG Agent initialized successfully!")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "MCP-Powered Agentic RAG",
        "version": "1.0.0",
        "description": "Local agentic RAG system using Model Context Protocol",
        "endpoints": {
            "query": "/query",
            "search": "/search",
            "add_documents": "/documents",
            "stats": "/stats",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if agent is None or vector_store is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    return {
        "status": "healthy",
        "vector_store_documents": vector_store.get_collection_stats()["document_count"]
    }


@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Query the RAG agent with optional context retrieval
    
    Args:
        request: QueryRequest with query, use_context, and n_results
        
    Returns:
        QueryResponse with answer and retrieved documents
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        result = agent.get_response(
            query=request.query,
            use_context=request.use_context,
            n_results=request.n_results
        )
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search_documents(request: SearchRequest):
    """
    Search for documents in the vector store
    
    Args:
        request: SearchRequest with query and n_results
        
    Returns:
        Search results with documents, IDs, and metadata
    """
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        results = vector_store.search(request.query, request.n_results)
        return {
            "query": request.query,
            "results": results,
            "count": len(results["documents"])
        }
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents")
async def add_documents(request: DocumentsRequest):
    """
    Add documents to the vector store
    
    Args:
        request: DocumentsRequest with documents, optional IDs and metadata
        
    Returns:
        Confirmation of documents added
    """
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        vector_store.add_documents(
            documents=request.documents,
            ids=request.ids,
            metadata=request.metadata
        )
        return {
            "status": "success",
            "documents_added": len(request.documents),
            "total_documents": vector_store.get_collection_stats()["document_count"]
        }
    except Exception as e:
        logger.error(f"Error adding documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get statistics about the vector store and system"""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        stats = vector_store.get_collection_stats()
        return {
            "vector_store": stats,
            "agent_config": {
                "model": agent.model if agent else "unknown",
                "ollama_url": agent.ollama_url if agent else "unknown",
                "max_tokens": agent.max_tokens if agent else 0,
                "temperature": agent.temperature if agent else 0.0
            }
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents")
async def clear_documents():
    """Clear all documents from the vector store"""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        vector_store.delete_collection()
        logger.info("Vector store cleared")
        return {"status": "success", "message": "All documents cleared"}
    except Exception as e:
        logger.error(f"Error clearing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Run the MCP server"""
    logger.info("Starting MCP-Powered Agentic RAG Server...")
    logger.info("Make sure Ollama is running at http://localhost:11434")
    logger.info("Server will be available at http://localhost:8000")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
