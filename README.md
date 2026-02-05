# LLM HV Search

A document search and chat application using Claude (Anthropic), OpenAI embeddings, FAISS vector search, and Streamlit.

## Project Structure

```
llm-hv-search/
├── src/                    # Source modules
│   ├── config.py          # Configuration
│   ├── llm.py             # Claude + OpenAI clients
│   ├── auth.py            # Authentication
│   ├── search.py          # FAISS search
│   ├── chat.py            # Chat handler with RAG
│   ├── excel.py           # Excel operations
│   ├── ui.py              # Streamlit UI
│   └── indexer.py         # Document indexing
├── data/indexes/          # FAISS indexes
├── DocumentosHR/          # HR documents
├── DocumentosQA/          # QA documents
├── excel_data/            # Excel files
├── app.py                 # Main application
├── indexer.py             # Indexer CLI
└── requirements.txt
```

## Quick Start

### 1. Setup

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file:

```env
# Claude (Anthropic) - for chat
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
CLAUDE_MODEL=claude-sonnet-4-20250514

# OpenAI - for embeddings
OPENAI_API_KEY=sk-xxxxx
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Users (format: username:password:role)
APP_USERS=admin:admin123:admin,user1:pass1:user
```

### 3. Index Documents

```bash
python indexer.py hr       # Index HR documents
python indexer.py qa       # Index QA documents
python indexer.py all      # Index both
```

### 4. Run

```bash
streamlit run app.py
```

## Features

### Document Q&A
- RAG-based question answering
- Searches HR and/or QA documents based on login status
- Conversation history

### Access Control
| Role | QA Docs | HR Docs | Excel |
|------|---------|---------|-------|
| Guest | ✅ | ❌ | ❌ |
| User | ✅ | ✅ | Own data |
| Admin | ✅ | ✅ | All data |

### Excel Commands
Logged-in users can edit Excel files via natural language:

```
"Update my status to completed in project_tracker.xlsx"
"Show my data in employee_data.xlsx"
"Set my progress to 75% in project_tracker.xlsx"
```

Admin users can also access other users' data:
```
"Show juan's data in employee_data.xlsx"
"Update maria's status to active in project_tracker.xlsx"
```

### Available Excel Files
- `employee_data.xlsx` - Employee info
- `project_tracker.xlsx` - Project status
- `time_tracking.xlsx` - Time sheets
- `performance_review.xlsx` - Reviews

## Deployment

### Streamlit Cloud

Add secrets in app settings:

```toml
ANTHROPIC_API_KEY = "sk-ant-api03-xxxxx"
OPENAI_API_KEY = "sk-xxxxx"
APP_USERS = "admin:admin123:admin,user1:pass1:user"
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude API key | Required |
| `OPENAI_API_KEY` | OpenAI API key (embeddings) | Required |
| `CLAUDE_MODEL` | Claude model name | claude-sonnet-4-20250514 |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | text-embedding-3-small |
| `APP_USERS` | User credentials | Required |

## Demo Mode

If API keys are not configured, the app runs in demo mode with simulated responses.

## License

Part of LLM Trabajo Final coursework.
