"""
Streamlit Frontend for MCP-Powered Agentic RAG System
Interactive web UI for querying the RAG agent
"""

import streamlit as st
import requests
import json
from typing import Dict, Any

# Page configuration
st.set_page_config(
    page_title="MCP RAG Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .response-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
    }
    .doc-box {
        background-color: #fffacd;
        padding: 12px;
        border-left: 4px solid #ffd700;
        margin: 10px 0;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.title("⚙️ Configuration")

api_url = st.sidebar.text_input(
    "API URL",
    value="http://localhost:8000",
    help="Base URL of the MCP RAG API server"
)

model_info = st.sidebar.empty()
health_status = st.sidebar.empty()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_count" not in st.session_state:
    st.session_state.doc_count = 0

# Functions
def check_health() -> Dict[str, Any]:
    """Check API health status"""
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def query_agent(query: str, use_context: bool, n_results: int) -> Dict[str, Any]:
    """Query the RAG agent"""
    try:
        response = requests.post(
            f"{api_url}/query",
            json={
                "query": query,
                "use_context": use_context,
                "n_results": n_results
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API server. Is it running?"}
    except Exception as e:
        return {"error": str(e)}

def get_stats() -> Dict[str, Any]:
    """Get system statistics"""
    try:
        response = requests.get(f"{api_url}/stats", timeout=5)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def add_documents(documents: list, ids: list = None) -> Dict[str, Any]:
    """Add documents to vector store"""
    try:
        response = requests.post(
            f"{api_url}/documents",
            json={
                "documents": documents,
                "ids": ids
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Header
st.markdown('<div class="main-header">🤖 MCP-Powered Agentic RAG</div>', 
            unsafe_allow_html=True)
st.markdown("Ask questions and get intelligent answers powered by RAG and LLMs")

# Check API health
health = check_health()
if health.get("status") == "healthy":
    health_status.success(f"✅ API Healthy ({health.get('vector_store_documents', 0)} documents)")
    st.session_state.doc_count = health.get('vector_store_documents', 0)
else:
    health_status.error(f"❌ API Error: {health.get('message', 'Unknown error')}")

# Get system stats
try:
    stats = get_stats()
    if "vector_store" in stats:
        model_info.info(f"Model: {stats['agent_config'].get('model', 'unknown')}")
except:
    pass

# Tabs for different features
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📚 Document Management", "📊 Statistics"])

# Tab 1: Chat
with tab1:
    st.subheader("Ask a Question")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_area(
            "Your question:",
            placeholder="What is the Model Context Protocol?",
            height=100
        )
    
    with col2:
        use_context = st.checkbox("Use Context", value=True, help="Retrieve documents before generating response")
        n_results = st.slider("Context Documents", 1, 10, 3, help="Number of documents to retrieve")
    
    # Submit button
    if st.button("🔍 Submit Query", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("Please enter a question")
        else:
            with st.spinner("Generating response..."):
                result = query_agent(query, use_context, n_results)
            
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                # Display response
                st.subheader("Response")
                st.markdown('<div class="response-box">', unsafe_allow_html=True)
                st.markdown(result.get("response", "No response"))
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Store in conversation history
                st.session_state.messages.append({
                    "role": "user",
                    "content": query
                })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result.get("response", "")
                })
                
                # Display context
                if use_context and result.get("retrieved_documents"):
                    st.subheader("📖 Retrieved Context")
                    for i, doc in enumerate(result["retrieved_documents"], 1):
                        with st.expander(f"Document {i}"):
                            st.write(doc[:500] + "..." if len(doc) > 500 else doc)
    
    # Conversation history
    if st.session_state.messages:
        st.divider()
        st.subheader("📝 Conversation History")
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.write(f"**You:** {message['content']}")
            else:
                st.write(f"**Agent:** {message['content']}")


# Tab 2: Document Management
with tab2:
    st.subheader("Manage Documents")
    
    management_tab1, management_tab2 = st.tabs(["Add Documents", "View Collection"])
    
    with management_tab1:
        st.write("Add new documents to the vector store")
        
        input_method = st.radio("Input method:", ["Text Input", "Paste Documents"], horizontal=True)
        
        if input_method == "Text Input":
            doc_text = st.text_area(
                "Enter document text:",
                placeholder="Paste your document content here...",
                height=200
            )
            
            if st.button("Add Document"):
                if doc_text.strip():
                    with st.spinner("Adding document..."):
                        result = add_documents([doc_text])
                    
                    if "error" not in result:
                        st.success(f"✅ Added document! Total documents: {result.get('total_documents', 0)}")
                        st.session_state.doc_count = result.get('total_documents', 0)
                    else:
                        st.error(f"Error: {result.get('error', 'Unknown error')}")
                else:
                    st.warning("Please enter document text")
        
        else:  # Paste Documents
            num_docs = st.number_input("Number of documents:", min_value=1, max_value=10, value=2)
            documents = []
            
            for i in range(num_docs):
                doc = st.text_area(
                    f"Document {i+1}:",
                    placeholder=f"Enter document {i+1} text...",
                    height=100,
                    key=f"doc_{i}"
                )
                if doc.strip():
                    documents.append(doc)
            
            if st.button("Add All Documents"):
                if documents:
                    with st.spinner("Adding documents..."):
                        result = add_documents(documents)
                    
                    if "error" not in result:
                        st.success(f"✅ Added {result.get('documents_added', 0)} documents!")
                        st.session_state.doc_count = result.get('total_documents', 0)
                    else:
                        st.error(f"Error: {result.get('error', 'Unknown error')}")
                else:
                    st.warning("Please enter at least one document")
    
    with management_tab2:
        if st.button("Refresh Statistics"):
            stats = get_stats()
            if "vector_store" in stats:
                st.info(f"**Collection:** {stats['vector_store']['collection_name']}")
                st.info(f"**Total Documents:** {stats['vector_store']['document_count']}")
                st.info(f"**Storage Location:** {stats['vector_store']['persist_dir']}")


# Tab 3: Statistics
with tab3:
    st.subheader("System Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Documents in Store", st.session_state.doc_count)
    
    with col2:
        st.metric("API Status", "✅ Active" if health.get("status") == "healthy" else "❌ Inactive")
    
    with col3:
        stats = get_stats()
        if "agent_config" in stats:
            st.metric("Model", stats['agent_config'].get('model', 'Unknown'))
    
    st.divider()
    
    # Detailed stats
    if "agent_config" in stats:
        st.subheader("Agent Configuration")
        st.json(stats['agent_config'])
    
    if "vector_store" in stats:
        st.subheader("Vector Store Configuration")
        st.json(stats['vector_store'])


# Footer
st.divider()
st.caption("MCP-Powered Agentic RAG System | Built with FastAPI, ChromaDB, and Ollama")
