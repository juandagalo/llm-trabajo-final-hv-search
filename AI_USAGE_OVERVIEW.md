# 🤖 AI Usage in Your LLM HV Search Application

## Overview
Your application uses **Azure OpenAI** (ChatGPT) in multiple strategic places to provide intelligent functionality. Here's exactly where and how AI is implemented:

## 🎯 AI Integration Points

### 1. **Document Q&A (RAG System)** 📚
**Location**: `src/core/chat_handler.py` (Lines 87-142)
**AI Models Used**: 
- **Chat Model**: `gpt-4.1-nano` (configurable)
- **Embeddings**: `text-embedding-3-small`

**What it does**:
```python
# Generates responses using context from documents
response = client.chat.completions.create(
    model=model,
    messages=temp_conversation  # Includes system prompt + context + user question
)
```

**Purpose**: Answers user questions by searching through HR and QA documents and generating contextual responses.

---

### 2. **Document Embeddings Creation** 🔍
**Location**: `src/core/indexer.py` (Lines 72-78)
**AI Model Used**: `text-embedding-3-small`

**What it does**:
```python
# Creates embeddings for document chunks during indexing
response = client.embeddings.create(
    input=file_chunks,
    model=deployment
)
embs = [d.embedding for d in response.data]
```

**Purpose**: Converts document text into vector embeddings for semantic search capabilities.

---

### 3. **Semantic Search** 🔎
**Location**: `src/core/search.py` (Lines 34-40)
**AI Model Used**: `text-embedding-3-small`

**What it does**:
```python
# Creates embedding for search queries
response = client.embeddings.create(
    input=[text],
    model=deployment
)
emb = np.array(response.data[0].embedding, dtype="float32")
```

**Purpose**: Converts user queries into embeddings to find similar document content using FAISS vector search.

---

### 4. **Excel Command Parsing** 📊
**Location**: `src/core/excel_manager.py` (Lines 356-365)
**AI Model Used**: `gpt-4.1-nano`

**What it does**:
```python
# Parses natural language Excel commands into structured JSON
response = client.chat.completions.create(
    model=get_chat_model(),
    messages=[
        {"role": "system", "content": "You are a JSON parser. Respond only with valid JSON."},
        {"role": "user", "content": extraction_prompt}
    ],
    temperature=0.1
)
```

**Purpose**: Understands natural language commands like "Update juan's status to completed" and extracts structured actions.

---

## 🔧 AI Configuration

### Azure OpenAI Settings
**Location**: `src/config/settings.py`
```python
# AI Models Configuration
AZURE_CHAT_MODEL = "gpt-4.1-nano"           # For conversations & parsing
AZURE_EMBEDDING_DEPLOYMENT = "text-embedding-3-small"  # For embeddings
AZURE_ENDPOINT = "https://pnl-maestria.openai.azure.com/"
```

### Client Management
**Location**: `src/core/azure_client.py`
- Centralized Azure OpenAI client configuration
- Handles authentication and model access
- Provides mock mode for demo purposes

---

## 🎪 AI Workflow Examples

### Example 1: Document Q&A Flow
1. **User asks**: "What are the QA testing best practices?"
2. **Search AI**: Creates embedding for query → Finds relevant documents
3. **Chat AI**: Generates response using found documents as context
4. **Result**: Contextual answer based on your document knowledge base

### Example 2: Excel Admin Command Flow
1. **Admin says**: "Update juan's status to completed in project_tracker.xlsx"
2. **Parsing AI**: Extracts: `{action: "update", target_user: "juan", column: "status", value: "completed", file: "project_tracker.xlsx"}`
3. **System**: Executes the parsed command with proper permissions
4. **Result**: Juan's status updated + confirmation message

### Example 3: Document Processing Flow
1. **System**: Processes HR/QA documents during indexing
2. **Embedding AI**: Converts text chunks into vectors
3. **FAISS**: Stores vectors for fast similarity search
4. **Result**: Searchable knowledge base ready for queries

---

## 🛡️ AI Security & Access Control

### Role-Based AI Responses
**Location**: `src/auth/authentication.py` (Lines 89-99)
```python
# Different system prompts based on user role
if role == "admin":
    return ("Eres un experto en recursos humanos... Además, tienes acceso administrativo completo...")
else:
    return ("Eres un experto en recursos humanos, selección de personal...")
```

### Access-Controlled Document Search
- **Guest users**: AI only searches QA documents
- **Logged users**: AI searches both QA and HR documents  
- **Admin users**: AI has full access + admin command parsing

---

## 🔄 Fallback & Demo Modes

### Mock AI Mode
When Azure OpenAI is not configured:
- **Document Q&A**: Returns demo responses
- **Embeddings**: Uses random vectors for demonstration
- **Excel Parsing**: Uses regex-based parsing instead of AI

**Location**: Multiple files check `is_mock_mode()` to provide fallbacks

---

## 💡 Key AI Features

### 1. **Conversational Memory** 🧠
- Maintains conversation history in session state
- AI responses consider previous context
- System prompts adapt based on user role

### 2. **Intelligent Command Understanding** 🗣️
- Natural language Excel commands
- Contextual admin vs personal operations
- Flexible command parsing with fallbacks

### 3. **Semantic Document Search** 📖
- Vector-based similarity search
- Multi-document context combination
- Relevance-ranked results

### 4. **Adaptive Responses** 🎭
- Different AI behavior for different user roles
- Access-level appropriate system prompts
- Context-aware document retrieval

---

## 🎯 Summary

**Your application uses AI in 4 critical areas:**
1. **💬 Conversational Q&A** - Main chat interface with document context
2. **🔍 Document Understanding** - Embeddings for semantic search
3. **📊 Command Parsing** - Natural language to structured actions
4. **🧠 Intelligent Responses** - Role-based and context-aware AI behavior

All AI functionality is **centrally managed**, **security-aware**, and **has fallback modes** for demonstration purposes. The AI integration makes your application truly intelligent and user-friendly! 🚀