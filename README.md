# MCP-Powered Agentic RAG System

A local, modular Retrieval-Augmented Generation (RAG) system using the Model Context Protocol (MCP) to connect an LLM to external tools like vector databases and document loaders.


<img src="/images/mcp-agentic-rag.gif" alt="description" style="width:100%; height:auto;" />

## Overview

This project implements an agentic RAG system that:
- **Retrieves** relevant documents from a local vector database (ChromaDB)
- **Augments** prompts with retrieved context
- **Generates** informed responses using a local LLM (Ollama)
- **Exposes** functionality via REST API with FastAPI

## Tech Stack

| Component | Tool/Library | Details |
|-----------|---|---|
| **Language Model** | Ollama | Local LLM inference (mistral, llama3, etc.) |
| **Agent Framework** | mcp + FastAPI | API server with tool registration |
| **RAG Pipeline** | LangChain + Custom | Context retrieval and prompt engineering |
| **Vector Store** | ChromaDB | Local, persistent vector database |
| **Embeddings** | SentenceTransformers | all-MiniLM-L6-v2 model |
| **File Handling** | pypdf, python-docx | PDF and document loading |
| **Frontend (Optional)** | Streamlit | Interactive web UI |
| **Environment** | Python 3.10+ | virtualenv or Conda |

## Project Structure

```
agentic-rag-mcp/
├── main.py                    # FastAPI MCP server
├── rag_agent.py              # Agent query logic and RAG orchestration
├── mcp_config.yaml           # Configuration file
├── requirements.txt          # Python dependencies
├── vector_store/             # Persisted ChromaDB vector store
├── data/
│   └── sample_docs/          # Sample documents for ingestion
└── tools/
    └── chromadb_tool.py      # Vector search tool implementation
```

## Installation & Setup

### 1. Clone and Create Virtual Environment

```bash
cd agentic-rag-mcp
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -U pip
pip install -r requirements.txt
```

### 3. Set Up Ollama

Download and install [Ollama](https://ollama.ai) from the official website.

Start the Ollama server:

```bash
# On the system terminal (not in virtual environment)
ollama serve
```

In another terminal, pull a model:

```bash
ollama pull mistral    # Recommended for RAG
# or
ollama pull llama3
```

Verify the server is running:

```bash
curl http://localhost:11434/api/tags
```

## Running the System

### Option 1: Chat Interface (Interactive)

Run the interactive chat loop:

```bash
python rag_agent.py
```

This will:
1. Load sample documents into the vector store
2. Start an interactive chat where you can ask questions
3. The agent will retrieve relevant documents and generate answers

Example interaction:
```
You: What is MCP?
Agent: The Model Context Protocol (MCP) enables modular tool use for AI agents by providing a standardized way to connect language models to external services...

[Used 2 retrieved documents as context]
```

### Option 2: API Server

Start the FastAPI MCP server:

```bash
python main.py
```

The server will be available at: `http://localhost:8000`

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Query Agent
```bash
POST /query
Content-Type: application/json

{
  "query": "What is artificial intelligence?",
  "use_context": true,
  "n_results": 3
}
```

#### Search Documents
```bash
POST /search
Content-Type: application/json

{
  "query": "MCP protocol",
  "n_results": 5
}
```

#### Add Documents
```bash
POST /documents
Content-Type: application/json

{
  "documents": [
    "Document text 1",
    "Document text 2"
  ],
  "ids": ["doc1", "doc2"],
  "metadata": [
    {"source": "file1.txt"},
    {"source": "file2.txt"}
  ]
}
```

#### Get Statistics
```bash
GET /stats
```

### Python Usage Examples

```python
from rag_agent import RAGAgent

# Initialize agent
agent = RAGAgent(
    ollama_url="http://localhost:11434",
    model="mistral"
)

# Get a response
result = agent.get_response("What is RAG?")
print(result["response"])
print(f"Retrieved {len(result['retrieved_documents'])} documents")
```

## Configuration

Edit `mcp_config.yaml` to customize:

- **LLM Settings**: Model, temperature, max tokens
- **Vector Store**: Embedding model, collection name
- **RAG**: Number of retrieved documents, similarity metric
- **Server**: Host, port, log level
- **Security**: API rate limits, authentication

## Adding Custom Documents

### Programmatically

```python
from tools.chromadb_tool import ChromaTool

tool = ChromaTool()
documents = [
    "Your document text 1",
    "Your document text 2"
]
tool.add_documents(documents, ids=["id1", "id2"])
```

### Via API

```bash
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{
    "documents": ["Document 1", "Document 2"],
    "ids": ["doc1", "doc2"]
  }'
```

## Optional Streamlit Frontend

Create `streamlit_app.py`:

```python
import streamlit as st
import requests

st.set_page_config(page_title="RAG Agent", layout="wide")
st.title("MCP-Powered Agentic RAG")

query = st.text_input("Ask a question:")

if query:
    response = requests.post(
        "http://localhost:8000/query",
        json={"query": query}
    )
    result = response.json()
    
    st.subheader("Response")
    st.write(result["response"])
    
    st.subheader("Retrieved Context")
    for i, doc in enumerate(result["retrieved_documents"], 1):
        st.write(f"**Doc {i}**: {doc[:200]}...")
```

Run Streamlit:
```bash
streamlit run streamlit_app.py
```

## Extensions & Future Work

- ✅ Basic RAG with ChromaDB
- ⬜ Web search tool integration
- ⬜ PDF document ingestion UI
- ⬜ Agent memory (conversation history)
- ⬜ Multi-modal support (images, tables)
- ⬜ Fine-tuning on domain-specific data
- ⬜ Structured output (JSON schemas)
- ⬜ Real-time streaming responses

## Troubleshooting

### "Connection refused" for Ollama
- Make sure Ollama server is running: `ollama serve`
- Check it's accessible: `curl http://localhost:11434/api/tags`

### ChromaDB embedding errors
- Ensure sentence-transformers is installed: `pip install sentence-transformers`
- First run downloads embeddings model (~30MB)

### Vector store not persisting
- Check `./vector_store/` directory exists and is writable
- Verify `persist_dir` in configuration matches actual path

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push and open a pull request

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Ollama Documentation](https://ollama.ai)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [LangChain RAG Guide](https://python.langchain.com/docs/use_cases/question_answering/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

