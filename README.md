# LLM Trabajo Final HV Search

A sophisticated document search and chat application using Azure OpenAI, FAISS vector search, and Streamlit for HR and QA document management.

## 🏗️ Project Structure

```
llm-trabajo-final-hv-search/
├── src/                           # Source code modules
│   ├── core/                      # Core business logic
│   │   ├── __init__.py
│   │   ├── azure_client.py        # Azure OpenAI client management
│   │   ├── indexer.py             # Document indexing functionality
│   │   ├── search.py              # FAISS search operations
│   │   └── rag.py                 # RAG (Retrieval-Augmented Generation)
│   ├── utils/                     # Utility functions
│   │   ├── __init__.py
│   │   ├── text_processing.py     # Text extraction and chunking
│   │   └── file_tracking.py       # File tracking utilities
│   ├── config/                    # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py            # Centralized configuration
│   └── __init__.py
├── data/                          # Data directory
│   └── indexes/                   # FAISS indexes and metadata
├── DocumentosHR/                  # HR documents folder
├── DocumentosQA/                  # QA documents folder
├── app.py                         # Streamlit web application
├── indexer_hr.py                  # HR document indexer script
├── indexer_qa.py                  # QA document indexer script
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your Azure OpenAI credentials:

```env
ENDPOINT=https://your-openai-instance.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-02-01
DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_CHAT_MODEL=gpt-4o
```

### 3. Index Documents

```bash
# Index HR documents
python indexer_hr.py

# Index QA documents  
python indexer_qa.py
```

### 4. Run the Application

```bash
streamlit run app.py
```

## 📋 Features

### ✅ **Modular Architecture**
- Clean separation of concerns
- Reusable components
- Easy to maintain and extend

### ✅ **Document Processing**
- PDF and text file support
- Intelligent text chunking
- File tracking and metadata

### ✅ **Vector Search**
- FAISS-based similarity search
- Azure OpenAI embeddings
- Cosine similarity scoring

### ✅ **RAG Implementation**
- Context-aware responses
- Mode-specific prompts (HR/QA)
- Conversation history management

### ✅ **User Interface**
- Interactive Streamlit chat interface
- Mode selection (HR/QA)
- Real-time status indicators
- File list viewing

### ✅ **Robust Configuration**
- Centralized settings management
- Environment variable support
- Mock mode for testing

## 🔧 Core Modules

### `src.core.azure_client`
Manages Azure OpenAI client configuration and provides singleton access.

### `src.core.indexer`
Handles document processing, embedding generation, and FAISS index creation.

### `src.core.search`
Provides document search functionality with similarity scoring.

### `src.core.rag`
Implements Retrieval-Augmented Generation for question answering.

### `src.utils.text_processing`
Text extraction, cleaning, and chunking utilities.

### `src.utils.file_tracking`
Tracks processed files and maintains metadata.

### `src.config.settings`
Centralized configuration management with environment variable support.

## 🎯 Usage Examples

### Indexing Documents

```python
from src.core.indexer import run_indexer

# Index HR documents
run_indexer(mode="hr", chunk_size=100, overlap=10)

# Index QA documents
run_indexer(mode="qa", chunk_size=150, overlap=15)
```

### Searching Documents

```python
from src.core.search import search

# Search HR documents
results = search("performance review process", k=5, mode="hr")

# Search QA documents
results = search("test automation", k=5, mode="qa")
```

### RAG Question Answering

```python
from src.core.rag import answer_question

conversation = []
answer = answer_question("What is the leave policy?", conversation, mode="hr")
```

## 📊 File Tracking

The system automatically tracks processed files:

- `data/indexes/chunks_hr_filenames.txt` - HR documents processed
- `data/indexes/chunks_qa_filenames.txt` - QA documents processed

## 🛡️ Error Handling

- Graceful fallback to mock mode when Azure credentials are missing
- Comprehensive error logging
- Defensive programming with safe dictionary access

## 🔄 Migration from Old Structure

The old files (`main.py`, `indexerHR.py`, `indexerQA.py`, etc.) have been refactored into the new modular structure. The new simplified scripts (`app.py`, `indexer_hr.py`, `indexer_qa.py`) provide the same functionality with cleaner code organization.

## 🧪 Testing

```bash
# Test the configuration
python -c "from src.config.settings import Config; print('✅ Config loaded')"

# Test Azure client
python -c "from src.core.azure_client import get_azure_client; print('✅ Azure client ready')"

# Test search functionality
python -c "from src.core.search import check_available_modes; print(check_available_modes())"
```

## 📝 Development

To add new features:

1. Add new modules in appropriate `src/` subdirectories
2. Update configuration in `src/config/settings.py` if needed
3. Create corresponding tests
4. Update this README

## 🤝 Contributing

1. Follow the established module structure
2. Add proper docstrings and type hints
3. Update configuration management for new settings
4. Test both real and mock modes

## 📄 License

This project is part of the LLM Trabajo Final coursework.