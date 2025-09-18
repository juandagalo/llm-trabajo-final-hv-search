"""
QA Document Indexer
Simplified script for indexing QA documents using the refactored module structure.
"""
import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.indexer import run_indexer


if __name__ == "__main__":
    """Run QA document indexing."""
    run_indexer(mode="qa")