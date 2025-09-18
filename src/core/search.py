"""
Search functionality for querying FAISS indexes and retrieving relevant documents.
"""
import os
import numpy as np
import pandas as pd
import faiss
from typing import Dict, List, Any

from ..config.settings import Config
from ..core.azure_client import get_azure_client, get_embedding_deployment, is_mock_mode
from ..utils.file_tracking import load_processed_files, get_filenames_path


class DocumentSearcher:
    """Handles document search operations using FAISS indexes."""
    
    def __init__(self):
        """Initialize the document searcher."""
        pass
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a single text."""
        if is_mock_mode():
            # Return mock embedding for demo
            emb = np.random.rand(1536).astype('float32')
            emb = np.ascontiguousarray(emb.reshape(1, -1))
            faiss.normalize_L2(emb)
            return emb
        
        client = get_azure_client()
        deployment = get_embedding_deployment()
        
        response = client.embeddings.create(
            input=[text],
            model=deployment
        )
        emb = np.array(response.data[0].embedding, dtype="float32")
        emb = np.ascontiguousarray(emb.reshape(1, -1))
        faiss.normalize_L2(emb)
        return emb
    
    def load_artifacts(self, mode: str):
        """
        Load FAISS index and chunks DataFrame for a specific mode.
        
        Args:
            mode: Mode ('hr' or 'qa')
            
        Returns:
            Tuple of (faiss_index, chunks_dataframe)
        """
        config = Config.get_mode_config(mode)
        
        if is_mock_mode():
            # Create mock data for demo
            if mode.lower() == "qa":
                mock_data = {
                    "text": [
                        "This document covers QA testing methodologies and best practices.",
                        "Information about software testing frameworks and automation tools.",
                        "Test case design and execution strategies for quality assurance.",
                        "Bug tracking and defect management processes.",
                        "Automated testing tools and continuous integration practices."
                    ]
                }
            else:  # hr mode
                mock_data = {
                    "text": [
                        "This is a sample HR document about hiring processes and candidate evaluation.",
                        "Sample content about performance reviews and employee development.",
                        "HR policies and procedures for remote work arrangements.",
                        "Employee onboarding and training documentation.",
                        "Compensation and benefits administration guidelines."
                    ]
                }
            
            df = pd.DataFrame(mock_data)
            
            # Create simple mock FAISS index
            dimension = 1536
            index = faiss.IndexFlatL2(dimension)
            mock_embeddings = np.random.rand(len(mock_data["text"]), dimension).astype('float32')
            faiss.normalize_L2(mock_embeddings)
            index.add(mock_embeddings)
            
            return index, df
        
        # Load real artifacts
        try:
            index = faiss.read_index(config['faiss_index_path'])
            df = pd.read_parquet(config['chunks_parquet_path'])
            
            # Ensure 'text' column exists
            if "text" not in df.columns:
                if len(df.columns) == 1:
                    df = df.rename(columns={df.columns[0]: "text"})
                else:
                    raise ValueError("Cannot identify text column in chunks data")
                    
        except FileNotFoundError as e:
            available_modes = self.get_available_modes()
            available = [m for m, info in available_modes.items() if info["available"]]
            
            if available:
                raise FileNotFoundError(f"No artifacts found for mode '{mode}'. "
                                      f"Available modes: {available}. "
                                      f"Missing file: {e}")
            else:
                raise FileNotFoundError(f"No indexes found for any mode. "
                                      f"Run indexerHR.py or indexerQA.py first.")
        
        return index, df
    
    def cosine_from_l2_distance(self, dist_sq: np.ndarray) -> np.ndarray:
        """
        Convert L2 squared distance between unit vectors to cosine similarity.
        For normalized vectors: ||a-b||^2 = 2(1 - cos_sim) => cos_sim = 1 - dist^2/2
        """
        return 1.0 - dist_sq / 2.0
    
    def search(self, query: str, k: int = 10, mode: str = "hr") -> pd.DataFrame:
        """
        Search for the k most similar documents to the query.
        
        Args:
            query: Search query text
            k: Number of results to return
            mode: Search mode ('hr' or 'qa')
            
        Returns:
            DataFrame with search results sorted by similarity
        """
        # print(f"Searching in {mode.upper()} mode")
        
        index, df = self.load_artifacts(mode)
        query_embedding = self.get_embedding(query)
        
        distances, indices = index.search(query_embedding, k)
        distances = distances[0]
        indices = indices[0]
        
        # Build results DataFrame
        results = df.iloc[indices].copy()
        results["cosine_similarity"] = self.cosine_from_l2_distance(distances)
        results["faiss_id"] = indices
        results["search_mode"] = mode.upper()
        
        # Sort by similarity (highest first)
        results = results.sort_values("cosine_similarity", ascending=False).reset_index(drop=True)
        
        # print(f"Found {len(results)} results in {mode.upper()} index")
        return results
    
    def get_available_modes(self) -> Dict[str, Dict[str, Any]]:
        """
        Check what search modes are available based on existing files.
        
        Returns:
            Dictionary with mode availability information
        """
        available_modes = {}
        
        for mode in ["hr", "qa"]:
            config = Config.get_mode_config(mode)
            
            # Check if index and parquet files exist
            index_exists = os.path.exists(config['faiss_index_path'])
            parquet_exists = os.path.exists(config['chunks_parquet_path'])
            available = index_exists and parquet_exists
            
            # Load processed files information
            processed_files = load_processed_files(config['filenames_path']) if available else []
            
            mode_info = {
                "available": available,
                "faiss_path": config['faiss_index_path'],
                "parquet_path": config['chunks_parquet_path'],
                "filenames_path": config['filenames_path'],
                "processed_files": processed_files,
                "file_count": len(processed_files),
                "description": (f"{mode.upper()} documents ({len(processed_files)} files indexed)" 
                              if available else f"{mode.upper()} documents (run indexer{mode.upper()}.py to create)")
            }
            
            available_modes[mode] = mode_info
        
        return available_modes


# Global searcher instance
_searcher = None


def get_searcher() -> DocumentSearcher:
    """Get the global document searcher instance."""
    global _searcher
    if _searcher is None:
        _searcher = DocumentSearcher()
    return _searcher


def search(query: str, k: int = 10, mode: str = "hr") -> pd.DataFrame:
    """
    Convenience function for document search.
    
    Args:
        query: Search query text
        k: Number of results to return
        mode: Search mode ('hr' or 'qa')
        
    Returns:
        DataFrame with search results
    """
    return get_searcher().search(query, k, mode)


def check_available_modes() -> Dict[str, Dict[str, Any]]:
    """
    Convenience function to check available search modes.
    
    Returns:
        Dictionary with mode availability information
    """
    return get_searcher().get_available_modes()