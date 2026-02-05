"""
Configuration management for the LLM HV Search application.
Centralizes all environment variables and configuration settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration class for all application settings."""
    
    # Claude (Anthropic) Configuration - for chat
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
    
    # OpenAI Configuration - for embeddings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Document Processing Configuration
    DEFAULT_CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 100))
    DEFAULT_CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 10))
    
    # Paths Configuration
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    INDEXES_DIR = DATA_DIR / "indexes"
    
    # HR Configuration
    HR_DOCUMENTS_FOLDER = os.getenv("HR_DOCUMENTS_FOLDER", str(BASE_DIR / "DocumentosHR"))
    HR_FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_HR_PATH", str(INDEXES_DIR / "faiss_index_hr.faiss"))
    HR_CHUNKS_PARQUET_PATH = os.getenv("CHUNKS_PARQUET_HR_PATH", str(INDEXES_DIR / "chunks_hr.parquet"))
    
    # QA Configuration  
    QA_DOCUMENTS_FOLDER = os.getenv("QA_DOCUMENTS_FOLDER", str(BASE_DIR / "DocumentosQA"))
    QA_FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_QA_PATH", str(INDEXES_DIR / "faiss_index_qa.faiss"))
    QA_CHUNKS_PARQUET_PATH = os.getenv("CHUNKS_PARQUET_QA_PATH", str(INDEXES_DIR / "chunks_qa.parquet"))
    
    @classmethod
    def get_mode_config(cls, mode: str) -> dict:
        """Get configuration for a specific mode (hr/qa)."""
        if mode.lower() == "qa":
            return {
                "documents_folder": cls.QA_DOCUMENTS_FOLDER,
                "faiss_index_path": cls.QA_FAISS_INDEX_PATH,
                "chunks_parquet_path": cls.QA_CHUNKS_PARQUET_PATH,
                "filenames_path": str(Path(cls.QA_CHUNKS_PARQUET_PATH).with_suffix("")) + "_filenames.txt"
            }
        else:  # hr mode (default)
            return {
                "documents_folder": cls.HR_DOCUMENTS_FOLDER,
                "faiss_index_path": cls.HR_FAISS_INDEX_PATH,
                "chunks_parquet_path": cls.HR_CHUNKS_PARQUET_PATH,
                "filenames_path": str(Path(cls.HR_CHUNKS_PARQUET_PATH).with_suffix("")) + "_filenames.txt"
            }
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.INDEXES_DIR.mkdir(exist_ok=True)
        
        # Ensure document folders exist
        Path(cls.HR_DOCUMENTS_FOLDER).mkdir(exist_ok=True)
        Path(cls.QA_DOCUMENTS_FOLDER).mkdir(exist_ok=True)
    
    @classmethod
    def validate_claude_config(cls) -> bool:
        """Validate that Claude (Anthropic) configuration is complete."""
        return cls.ANTHROPIC_API_KEY is not None
    
    @classmethod
    def validate_openai_config(cls) -> bool:
        """Validate that OpenAI configuration for embeddings is complete."""
        return cls.OPENAI_API_KEY is not None
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is complete."""
        return cls.validate_claude_config() and cls.validate_openai_config()


# Ensure directories exist on import
Config.ensure_directories()