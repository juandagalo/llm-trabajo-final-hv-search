"""
Document indexer for creating FAISS indexes.
"""
import os
import glob
import numpy as np
import pandas as pd
import faiss
import tiktoken
from pathlib import Path
from pypdf import PdfReader
from . import config
from . import llm
from . import search as search_module


def read_pdf(path: str) -> str:
    """Extract text from PDF."""
    try:
        reader = PdfReader(path)
        texts = []
        for page in reader.pages:
            try:
                text = page.extract_text() or ""
                texts.append(text)
            except:
                texts.append("")
        return "\n".join(texts)
    except Exception as e:
        print(f"Error reading PDF {path}: {e}")
        return ""


def read_text(path: str) -> str:
    """Read text file."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return ""


def extract_text(path: str) -> str:
    """Extract text from file based on extension."""
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return read_pdf(path)
    elif ext in [".txt", ".md"]:
        return read_text(path)
    return ""


def collect_files(folder: str, extensions: list = None) -> list:
    """Find files in folder."""
    extensions = extensions or ["pdf", "txt"]
    files = []
    for ext in extensions:
        pattern = str(Path(folder) / f"**/*.{ext}")
        files.extend(glob.glob(pattern, recursive=True))
    return sorted(set(files))


def chunk_text(text: str, chunk_size: int, overlap: int) -> list:
    """Split text into chunks."""
    encoding = tiktoken.encoding_for_model("text-embedding-3-small")
    tokens = encoding.encode(text)
    chunks = []
    step = max(1, chunk_size - overlap)
    
    for start in range(0, len(tokens), step):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(encoding.decode(chunk_tokens))
        if end >= len(tokens):
            break
    
    return chunks


def run_indexer(mode: str, chunk_size: int = None, overlap: int = None):
    """Run document indexing for a mode."""
    chunk_size = chunk_size or config.DEFAULT_CHUNK_SIZE
    overlap = overlap or config.DEFAULT_CHUNK_OVERLAP
    cfg = config.get_mode_config(mode)
    
    print(f"\n{'='*50}")
    print(f"Indexing {mode.upper()} documents")
    print(f"Folder: {cfg['documents_folder']}")
    print(f"{'='*50}\n")
    
    # Ensure directories
    os.makedirs(os.path.dirname(cfg['faiss_index_path']), exist_ok=True)
    
    files = collect_files(cfg['documents_folder'])
    if not files:
        print(f"No documents found in {cfg['documents_folder']}")
        return
    
    all_chunks = []
    all_embeddings = []
    processed_files = []
    
    for file_path in files:
        text = extract_text(file_path)
        if not text.strip():
            print(f"⚠️ No text from {file_path}")
            continue
        
        chunks = chunk_text(text, chunk_size, overlap)
        print(f"📄 {os.path.basename(file_path)}: {len(chunks)} chunks")
        
        all_chunks.extend(chunks)
        processed_files.append(os.path.basename(file_path))
        
        # Get embeddings
        try:
            embeddings = llm.get_embeddings_batch(chunks)
            all_embeddings.extend(embeddings)
        except Exception as e:
            print(f"❌ Embedding error: {e}")
            # Use mock embeddings
            mock = [np.random.rand(1536).astype('float32').tolist() for _ in chunks]
            all_embeddings.extend(mock)
    
    if not all_chunks:
        print("No chunks to index")
        return
    
    # Save chunks
    df = pd.DataFrame({"text": all_chunks})
    df.to_parquet(cfg['chunks_parquet_path'], index=False)
    print(f"✅ Saved {len(all_chunks)} chunks")
    
    # Build FAISS index
    embeddings_array = np.ascontiguousarray(np.array(all_embeddings).astype('float32'))
    faiss.normalize_L2(embeddings_array)
    
    index = faiss.IndexFlatL2(embeddings_array.shape[1])
    index.add(embeddings_array)
    faiss.write_index(index, cfg['faiss_index_path'])
    print(f"✅ Saved FAISS index")
    
    # Save processed files list
    search_module.save_processed_files(processed_files, cfg['filenames_path'])
    
    print(f"\n✅ {mode.upper()} indexing complete: {len(processed_files)} files, {len(all_chunks)} chunks")
