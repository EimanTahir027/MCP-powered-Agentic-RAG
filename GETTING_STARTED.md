# Getting Started Guide - MCP-Powered Agentic RAG

## ⚡ Quick Start (5 minutes)

### Prerequisites
- Python 3.10 or higher
- Ollama installed from [ollama.ai](https://ollama.ai)
- Git (optional)

### Step 1: Install Dependencies

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Start Ollama

**In a separate terminal** (do NOT activate venv):

```bash
# Windows/macOS/Linux
ollama serve

# In another terminal, download a model
ollama pull mistral
```

Verify it's working:
```bash
curl http://localhost:11434/api/tags
```

### Step 3: Run the System

Choose one of three ways:

**Option A: Interactive Chat** (Simplest)
```bash
python rag_agent.py
```

**Option B: API Server** (For integration)
```bash
python main.py
# Server runs at http://localhost:8000
```

**Option C: Web UI** (Most user-friendly)
```bash
# Terminal 1: Start API server
python main.py

# Terminal 2: Start Streamlit
streamlit run streamlit_app.py
# Opens at http://localhost:8501
```

---

## 📋 Complete Setup Guide

### Environment Setup

1. **Navigate to project directory:**
   ```bash
   cd path/to/MCP-powered-Agentic-RAG
   ```

2. **Create virtual environment:**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Upgrade pip and install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Ollama Setup

1. **Install Ollama:**
   - Download from https://ollama.ai
   - Follow OS-specific installation instructions
   - Restart your computer if prompted

2. **Start Ollama server:**
   ```bash
   ollama serve
   ```
   
   You should see:
   ```
   Loaded weights from...
   Listening on 127.0.0.1:11434
   ```

3. **Pull a model (in another terminal):**
   ```bash
   # Recommended for RAG (4GB)
   ollama pull mistral
   
   # Or try other models
   ollama pull llama3           # 4.7GB
   ollama pull neural-chat       # 3.8GB
   ```

4. **Verify setup:**
   ```bash
   curl http://localhost:11434/api/tags
   ```
   
   Expected output:
   ```json
   {
     "models": [
       {
         "name": "mistral:latest",
         "modified_at": "2024-01-15T...",
         ...
       }
     ]
   }
   ```

---

## 🚀 Running the System

### Method 1: Interactive Chat (Easiest)

```bash
# Activate virtual environment (if not already active)
python rag_agent.py
```

The system will:
- Load sample documents automatically
- Start an interactive prompt
- Each question is answered using RAG

Example:
```
You: What is Artificial Intelligence?
Agent: Artificial Intelligence (AI) is the development of computer systems 
       capable of performing tasks that typically require human intelligence...

[Used 3 retrieved documents as context]

You: quit
Exiting chat. Goodbye!
```

Commands:
- `quit` or `exit` - Stop the chat
- `reload` - Reload sample documents
- Any other text - Question to ask

### Method 2: API Server (For Integration)

**Terminal 1: Start server**
```bash
python main.py
```

You'll see:
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: RAG Agent initialized successfully!
```

**Terminal 2: Query the API**

```bash
# Health check
curl http://localhost:8000/health

# Query with context
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is MCP?",
    "use_context": true,
    "n_results": 3
  }'
```

### Method 3: Web UI (Most User-Friendly)

**Terminal 1: Start API server**
```bash
python main.py
```

**Terminal 2: Start Streamlit**
```bash
streamlit run streamlit_app.py
```

- Opens automatically at http://localhost:8501
- User-friendly chat interface
- Document management
- System statistics dashboard

---

## 🧪 Testing the System

### Quick Test Script

```bash
python quickstart.py
```

Menu options:
1. Chat Interface
2. API Server
3. Streamlit Frontend
4. Test Vector Store
5. Load Sample Documents
6. System Info

### Manual Testing

```python
# test_system.py
from rag_agent import RAGAgent
from tools.chromadb_tool import load_sample_documents

# Initialize
agent = RAGAgent()

# Load sample documents if needed
if agent.vector_store.get_collection_stats()["document_count"] == 0:
    load_sample_documents(agent.vector_store)

# Test query
result = agent.get_response("What is the Model Context Protocol?")
print(f"Answer: {result['response']}")
print(f"Sources: {len(result['retrieved_documents'])} documents")
```

Run it:
```bash
python test_system.py
```

---

## 📚 Adding Your Own Documents

### Method 1: Programmatically

```python
from tools.chromadb_tool import ChromaTool

tool = ChromaTool()

documents = [
    "Your document text 1",
    "Your document text 2",
    "Your document text 3"
]

metadata = [
    {"source": "document1.txt", "category": "general"},
    {"source": "document2.txt", "category": "technical"},
    {"source": "document3.txt", "category": "general"}
]

tool.add_documents(documents, metadata=metadata)
```

### Method 2: Via API

```bash
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "Document content 1",
      "Document content 2"
    ],
    "metadata": [
      {"source": "file1.txt"},
      {"source": "file2.txt"}
    ]
  }'
```

### Method 3: Load from File

```python
# Load text file
with open("my_document.txt", "r") as f:
    content = f.read()

tool = ChromaTool()
tool.add_documents([content], ids=["my_doc"])
```

---

## 🔧 Configuration

### Basic Configuration

Edit `mcp_config.yaml`:

```yaml
llm:
  model: "mistral"  # or llama3, neural-chat
  temperature: 0.7  # 0=deterministic, 1=creative
  
rag:
  n_results_default: 3  # documents to retrieve
```

### Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:
```
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=mistral
VECTOR_STORE_PATH=./vector_store
```

---

## 🐛 Troubleshooting

### Problem: "Connection refused" when querying

**Solution:**
- Ensure Ollama is running: `ollama serve`
- Check URL is correct: `curl http://localhost:11434/api/tags`

### Problem: No documents found

**Solution:**
```bash
# Reload sample documents
python rag_agent.py
# Then type: reload
```

Or programmatically:
```python
from tools.chromadb_tool import ChromaTool, load_sample_documents
tool = ChromaTool()
load_sample_documents(tool)
```

### Problem: Slow responses

**Solutions:**
1. Use a faster model:
   ```bash
   ollama pull mistral  # Faster than llama3
   ```
2. Reduce document count:
   ```bash
   curl -X DELETE http://localhost:8000/documents
   ```
3. Reduce results:
   ```python
   agent.get_response(query, n_results=2)  # Instead of 3
   ```

### Problem: Out of memory

**Solution:**
- Use a smaller model: `ollama pull mistral`
- Close other applications
- Reduce `n_results` parameter

### Problem: "Service not initialized"

**Solution:**
- Restart the server: `python main.py`
- Check that ChromaDB and Ollama are accessible

---

## 📖 Documentation

- **README.md** - Overview and features
- **API.md** - Complete API reference
- **mcp_config.yaml** - Configuration options
- **GETTING_STARTED.md** - This file

---

## 💡 Common Use Cases

### Case 1: Ask Questions About Your Documents

```python
from rag_agent import RAGAgent

agent = RAGAgent()

# Add your documents
documents = [
    "Your company policy document...",
    "Your technical documentation..."
]
agent.vector_store.add_documents(documents)

# Ask questions
result = agent.get_response("What is the company vacation policy?")
print(result["response"])
```

### Case 2: Build a Chatbot

```bash
# Use Streamlit UI
streamlit run streamlit_app.py
```

### Case 3: Integrate with Another Application

```bash
# Start API server
python main.py

# Use from your app
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"query": "What is X?"}
)
answer = response.json()["response"]
```

### Case 4: Process Large Document Collections

```python
from tools.chromadb_tool import ChromaTool
import os

tool = ChromaTool()

# Process all files in a directory
for filename in os.listdir("documents/"):
    with open(f"documents/{filename}", "r") as f:
        content = f.read()
        tool.add_documents([content], ids=[filename])
```

---

## 📊 Performance Tips

| Operation | Typical Time | Tips |
|-----------|--------------|------|
| Query with context | 5-30s | Increase timeout if needed |
| Search | 0.5-2s | Increase with more documents |
| Add document | 1-5s | Batch add multiple docs |
| Health check | 0.1s | Should be instant |

---

## 🆘 Getting Help

1. **Check logs:**
   - Console output while running
   - Check `logs/rag_agent.log` if enabled

2. **Test individual components:**
   ```bash
   python -c "import chromadb; print('ChromaDB OK')"
   python -c "import ollama; print('Ollama OK')"
   ```

3. **Verify Ollama:**
   ```bash
   ollama list
   curl http://localhost:11434/api/tags
   ```

4. **Check configuration:**
   ```bash
   python quickstart.py
   # Choose option 6: Show System Info
   ```

---

## 🎓 Next Steps

After getting the basic system running:

1. **Customize Configuration:**
   - Edit `mcp_config.yaml`
   - Adjust model, temperature, context count

2. **Add Real Documents:**
   - Load your own documents
   - Test RAG performance

3. **Extend Functionality:**
   - Add web search tool
   - Integrate with external APIs
   - Add memory/conversation history

4. **Deploy:**
   - Use production WSGI server (gunicorn)
   - Add authentication
   - Configure rate limiting

---

## 📝 Example Queries to Try

After loading sample documents:

```
What is Artificial Intelligence?
Explain the Model Context Protocol
What are vector databases?
How does Retrieval-Augmented Generation work?
What is Deep Learning?
Tell me about the applications of AI
What is Natural Language Processing?
```

---

## 🎉 Success!

You now have a fully functional MCP-powered Agentic RAG system!

- ✅ Local LLM inference (Ollama)
- ✅ Vector database (ChromaDB)
- ✅ API server (FastAPI)
- ✅ Interactive chat interface
- ✅ Web UI (Streamlit)

Happy querying! 🚀
