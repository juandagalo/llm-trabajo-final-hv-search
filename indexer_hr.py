"""
HR Document Indexer
Simplified script for indexing HR documents using the refactored module structure.
"""
import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.indexer import run_indexer


if __name__ == "__main__":
    """Run HR document indexing."""
    run_indexer(mode="hr", chunk_size=100, overlap=10)