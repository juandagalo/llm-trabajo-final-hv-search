"""
Document search using FAISS indexes.
"""
import os
import numpy as np
import pandas as pd
import faiss
from . import config
from . import llm


def load_processed_files(filenames_path: str) -> list:
    """Load list of processed files."""
    try:
        if not os.path.exists(filenames_path):
            return []
        with open(filenames_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except:
        return []


def save_processed_files(filenames: list, output_path: str):
    """Save list of processed files."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Processed files ({len(filenames)} total)\n\n")
        for filename in sorted(filenames):
            f.write(f"{filename}\n")


def load_index(mode: str):
    """Load FAISS index and chunks for a mode."""
    cfg = config.get_mode_config(mode)
    
    if llm.is_mock_mode():
        # Mock data
        texts = [
            f"Sample {mode.upper()} document about testing." if mode == "qa" 
            else f"Sample {mode.upper()} document about HR."
        ] * 5
        df = pd.DataFrame({"text": texts})
        index = faiss.IndexFlatL2(1536)
        mock_emb = np.random.rand(5, 1536).astype('float32')
        faiss.normalize_L2(mock_emb)
        index.add(mock_emb)
        return index, df
    
    index = faiss.read_index(cfg['faiss_index_path'])
    df = pd.read_parquet(cfg['chunks_parquet_path'])
    
    if "text" not in df.columns and len(df.columns) == 1:
        df = df.rename(columns={df.columns[0]: "text"})
    
    return index, df


def search(query: str, mode: str = "hr", k: int = 10) -> pd.DataFrame:
    """Search for similar documents."""
    index, df = load_index(mode)
    query_emb = llm.get_embedding(query)
    
    distances, indices = index.search(query_emb, k)
    
    results = df.iloc[indices[0]].copy()
    results["cosine_similarity"] = 1.0 - distances[0] / 2.0  # L2 to cosine
    results["search_mode"] = mode.upper()
    
    return results.sort_values("cosine_similarity", ascending=False).reset_index(drop=True)


def check_available_modes() -> dict:
    """Check which search modes are available."""
    modes = {}
    for mode in ["hr", "qa"]:
        cfg = config.get_mode_config(mode)
        available = (os.path.exists(cfg['faiss_index_path']) and 
                    os.path.exists(cfg['chunks_parquet_path']))
        
        processed_files = load_processed_files(cfg['filenames_path']) if available else []
        
        modes[mode] = {
            "available": available,
            "file_count": len(processed_files),
            "processed_files": processed_files,
            "description": f"{mode.upper()} ({len(processed_files)} files)" if available else f"{mode.upper()} (not indexed)"
        }
    return modes
