# MCP-Powered Agentic RAG - API Documentation

## Overview

This document provides complete API reference for the MCP-Powered Agentic RAG system FastAPI server.

**Base URL:** `http://localhost:8000`  
**API Version:** 1.0.0

## Table of Contents

1. [Authentication](#authentication)
2. [Common Response Formats](#common-response-formats)
3. [Endpoints](#endpoints)
4. [Error Handling](#error-handling)
5. [Examples](#examples)

## Authentication

Currently, the API does not require authentication. For production deployments, consider enabling token-based authentication in `mcp_config.yaml`.

## Common Response Formats

### Success Response

```json
{
  "status": "success",
  "data": {},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Endpoints

### 1. GET `/` - API Information

Returns general information about the API.

**Request:**
```bash
GET /
```

**Response:**
```json
{
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
```

### 2. GET `/health` - Health Check

Checks the health status of the API and vector store.

**Request:**
```bash
GET /health
```

**Response (Success - 200):**
```json
{
  "status": "healthy",
  "vector_store_documents": 42
}
```

**Response (Error - 503):**
```json
{
  "detail": "Service not initialized"
}
```

### 3. POST `/query` - Query Agent

Query the RAG agent with context retrieval and LLM reasoning.

**Request:**
```bash
POST /query
Content-Type: application/json

{
  "query": "What is the Model Context Protocol?",
  "use_context": true,
  "n_results": 3
}
```

**Request Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| query | string | Yes | - | The user's question |
| use_context | boolean | No | true | Whether to retrieve context documents |
| n_results | integer | No | 3 | Number of documents to retrieve (1-10) |

**Response (Success - 200):**
```json
{
  "query": "What is the Model Context Protocol?",
  "response": "The Model Context Protocol (MCP) is a standardized way to connect language models to external services...",
  "retrieved_documents": [
    "MCP enables modular tool use for AI agents...",
    "The protocol provides clean separation of concerns..."
  ],
  "context_used": true,
  "model": "mistral"
}
```

**Response (Error - 500):**
```json
{
  "detail": "Error calling Ollama: Connection refused"
}
```

### 4. POST `/search` - Search Documents

Search for documents similar to a query using semantic search.

**Request:**
```bash
POST /search
Content-Type: application/json

{
  "query": "vector databases",
  "n_results": 5
}
```

**Request Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| query | string | Yes | - | Search query |
| n_results | integer | No | 3 | Number of results to return |

**Response (Success - 200):**
```json
{
  "query": "vector databases",
  "results": {
    "documents": [
      "Vector databases like ChromaDB store embeddings...",
      "ChromaDB enables efficient semantic search..."
    ],
    "ids": ["doc_1", "doc_2"],
    "distances": [0.15, 0.22],
    "metadatas": [
      {"source": "sample_docs/ai_fundamentals.txt"},
      {"source": "sample_docs/ai_fundamentals.txt"}
    ]
  },
  "count": 2
}
```

### 5. POST `/documents` - Add Documents

Add new documents to the vector store.

**Request:**
```bash
POST /documents
Content-Type: application/json

{
  "documents": [
    "Artificial Intelligence is revolutionizing many industries...",
    "Deep learning uses neural networks with multiple layers..."
  ],
  "ids": ["doc1", "doc2"],
  "metadata": [
    {"source": "article1.txt"},
    {"source": "article2.txt"}
  ]
}
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| documents | array | Yes | List of document texts |
| ids | array | No | Document IDs (auto-generated if not provided) |
| metadata | array | No | List of metadata objects for each document |

**Response (Success - 200):**
```json
{
  "status": "success",
  "documents_added": 2,
  "total_documents": 44
}
```

### 6. GET `/stats` - System Statistics

Get statistics about the vector store and agent configuration.

**Request:**
```bash
GET /stats
```

**Response (Success - 200):**
```json
{
  "vector_store": {
    "collection_name": "documents",
    "document_count": 42,
    "persist_dir": "./vector_store"
  },
  "agent_config": {
    "model": "mistral",
    "ollama_url": "http://localhost:11434",
    "max_tokens": 1024,
    "temperature": 0.7
  }
}
```

### 7. DELETE `/documents` - Clear Documents

Delete all documents from the vector store (destructive operation).

**Request:**
```bash
DELETE /documents
```

**Response (Success - 200):**
```json
{
  "status": "success",
  "message": "All documents cleared"
}
```

**Warning:** This operation permanently deletes all documents in the vector store. It cannot be undone without reimporting documents.

## Error Handling

### Common Error Codes

| Code | Message | Cause | Solution |
|------|---------|-------|----------|
| 400 | Bad Request | Invalid request format | Check JSON syntax and field types |
| 404 | Not Found | Endpoint doesn't exist | Verify the endpoint URL |
| 500 | Internal Server Error | Server-side error | Check server logs |
| 503 | Service Unavailable | Service not initialized | Restart the server |
| 504 | Gateway Timeout | LLM processing taking too long | Increase timeout or check Ollama |

### Error Response Format

```json
{
  "detail": "Detailed error message explaining what went wrong"
}
```

## Examples

### Example 1: Complete RAG Query Flow

```bash
# 1. Check health
curl http://localhost:8000/health

# 2. Add documents
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "Artificial Intelligence enables machines to learn from data."
    ],
    "ids": ["doc1"],
    "metadata": [{"source": "article.txt"}]
  }'

# 3. Query the agent
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is artificial intelligence?",
    "use_context": true,
    "n_results": 3
  }'

# 4. Get statistics
curl http://localhost:8000/stats
```

### Example 2: Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

# Query with context
response = requests.post(
    f"{BASE_URL}/query",
    json={
        "query": "How does RAG work?",
        "use_context": True,
        "n_results": 5
    }
)

result = response.json()
print(f"Answer: {result['response']}")
print(f"Sources: {len(result['retrieved_documents'])} documents")
```

### Example 3: JavaScript/Node.js Client

```javascript
const baseUrl = 'http://localhost:8000';

// Query the agent
async function queryAgent(query) {
  const response = await fetch(`${baseUrl}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      use_context: true,
      n_results: 3
    })
  });

  return await response.json();
}

// Usage
queryAgent('What is MCP?').then(result => {
  console.log('Response:', result.response);
  console.log('Documents:', result.retrieved_documents);
});
```

### Example 4: cURL with File Input

```bash
# Add documents from a text file
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "documents": [
    "$(cat document.txt)"
  ],
  "metadata": [
    {"source": "document.txt", "date": "2024-01-15"}
  ]
}
EOF
```

## Rate Limiting

The API applies rate limiting to prevent abuse. Default limits:
- **60 requests per minute** per IP address

Limits can be configured in `mcp_config.yaml`.

## Performance Considerations

### Query Performance
- **Context Retrieval:** 100-500ms depending on vector store size
- **LLM Inference:** 2-30s depending on response length (Ollama local inference)
- **Total Query Time:** 2-40 seconds typically

### Optimization Tips
1. Reduce `n_results` if not needed
2. Use smaller models for faster inference (e.g., mistral vs llama3-70b)
3. Keep vector store collections reasonably sized
4. Use `use_context: false` for quick responses without retrieval

## Best Practices

1. **Error Handling:** Always check HTTP status codes and handle errors gracefully
2. **Timeouts:** Set client timeouts to at least 60 seconds for LLM queries
3. **Document Management:** Clean up unused documents periodically
4. **Monitoring:** Track API response times and error rates
5. **Security:** In production, enable authentication and use HTTPS

## Troubleshooting

### "Service not initialized" Error
- Ensure the server has fully started
- Check that ChromaDB and Ollama are accessible

### "Connection refused" for Ollama
- Verify Ollama is running: `ollama serve`
- Check Ollama URL is correct in config

### Slow Query Response
- Check Ollama server isn't overloaded
- Reduce `n_results` parameter
- Try a faster model (mistral is faster than llama3)

## Version History

### v1.0.0 (Current)
- Initial release
- Core RAG functionality
- ChromaDB integration
- Ollama support
- FastAPI server

### Planned Future Versions
- v1.1.0: Web search integration
- v1.2.0: Multi-modal support
- v2.0.0: Advanced agent capabilities
