"""
Configuration for LLM HV Search application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
INDEXES_DIR = DATA_DIR / "indexes"

# Claude (Anthropic) - for chat
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")

# OpenAI - for embeddings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# Document processing
DEFAULT_CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 100))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 10))

# HR Configuration
HR_DOCUMENTS_FOLDER = os.getenv("HR_DOCUMENTS_FOLDER", str(BASE_DIR / "DocumentosHR"))
HR_FAISS_INDEX_PATH = str(INDEXES_DIR / "faiss_index_hr.faiss")
HR_CHUNKS_PARQUET_PATH = str(INDEXES_DIR / "chunks_hr.parquet")

# QA Configuration
QA_DOCUMENTS_FOLDER = os.getenv("QA_DOCUMENTS_FOLDER", str(BASE_DIR / "DocumentosQA"))
QA_FAISS_INDEX_PATH = str(INDEXES_DIR / "faiss_index_qa.faiss")
QA_CHUNKS_PARQUET_PATH = str(INDEXES_DIR / "chunks_qa.parquet")


def get_mode_config(mode: str) -> dict:
    """Get configuration for a specific mode (hr/qa)."""
    if mode.lower() == "qa":
        return {
            "documents_folder": QA_DOCUMENTS_FOLDER,
            "faiss_index_path": QA_FAISS_INDEX_PATH,
            "chunks_parquet_path": QA_CHUNKS_PARQUET_PATH,
            "filenames_path": QA_CHUNKS_PARQUET_PATH.replace(".parquet", "_filenames.txt")
        }
    else:
        return {
            "documents_folder": HR_DOCUMENTS_FOLDER,
            "faiss_index_path": HR_FAISS_INDEX_PATH,
            "chunks_parquet_path": HR_CHUNKS_PARQUET_PATH,
            "filenames_path": HR_CHUNKS_PARQUET_PATH.replace(".parquet", "_filenames.txt")
        }


def ensure_directories():
    """Ensure all required directories exist."""
    DATA_DIR.mkdir(exist_ok=True)
    INDEXES_DIR.mkdir(exist_ok=True)
    Path(HR_DOCUMENTS_FOLDER).mkdir(exist_ok=True)
    Path(QA_DOCUMENTS_FOLDER).mkdir(exist_ok=True)


# Ensure directories on import
ensure_directories()
