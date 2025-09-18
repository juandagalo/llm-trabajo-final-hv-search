"""
Document indexing functionality for creating FAISS indexes and embeddings.
"""
import os
import pandas as pd
import numpy as np
import faiss
from typing import List, Tuple
from pathlib import Path

from ..config.settings import Config
from ..core.azure_client import get_azure_client, get_embedding_deployment, is_mock_mode
from ..utils.text_processing import collect_files, extract_text_from_file, chunk_text
from ..utils.file_tracking import save_processed_files, get_filenames_path


class DocumentIndexer:
    """Handles document indexing and FAISS index creation."""
    
    def __init__(self, mode: str, chunk_size: int = None, overlap: int = None):
        """
        Initialize the document indexer.
        
        Args:
            mode: Mode ('hr' or 'qa')
            chunk_size: Size of text chunks in tokens
            overlap: Overlap between chunks in tokens
        """
        self.mode = mode.lower()
        self.config = Config.get_mode_config(self.mode)
        self.chunk_size = chunk_size or Config.DEFAULT_CHUNK_SIZE
        self.overlap = overlap or Config.DEFAULT_CHUNK_OVERLAP
        
        # Ensure output directories exist
        os.makedirs(os.path.dirname(self.config['faiss_index_path']), exist_ok=True)
        os.makedirs(os.path.dirname(self.config['chunks_parquet_path']), exist_ok=True)
    
    def process_documents(self) -> Tuple[List[str], List[List[float]]]:
        """
        Process documents from the configured folder.
        
        Returns:
            Tuple of (chunks, embeddings)
        """
        client = get_azure_client()
        deployment = get_embedding_deployment()
        
        chunks = []
        embeddings = []
        processed_files = []
        
        files_to_process = collect_files(self.config['documents_folder'])
        
        if not files_to_process:
            print(f"No documents found in {self.config['documents_folder']}")
            return chunks, embeddings
        
        for file_path in files_to_process:
            file_text = extract_text_from_file(file_path)
            if not file_text.strip():
                print(f"Warning: No text extracted from {file_path}")
                continue
                
            file_chunks = chunk_text(file_text, self.chunk_size, self.overlap)
            print(f'Document: {file_path}, generated {len(file_chunks)} chunks')
            
            chunks.extend(file_chunks)
            processed_files.append(os.path.basename(file_path))
            
            if client and not is_mock_mode():
                try:
                    response = client.embeddings.create(
                        input=file_chunks,
                        model=deployment
                    )
                    embs = [d.embedding for d in response.data]
                except Exception as e:
                    print(f"Error creating embeddings for {file_path}: {e}")
                    print("Falling back to mock embeddings")
                    embs = [np.random.rand(1536).astype('float32').tolist() for _ in file_chunks]
            else:
                # Mock mode embeddings
                embs = [np.random.rand(1536).astype('float32').tolist() for _ in file_chunks]
                if chunks:  # Only show warning once
                    print("⚠️  Using mock embeddings (demo mode)")
            
            embeddings.extend(embs)
        
        # Save the list of processed files
        if processed_files:
            save_processed_files(processed_files, self.config['filenames_path'])
        
        return chunks, embeddings
    
    def build_and_save_index(self, chunks: List[str], embeddings: List[List[float]]) -> None:
        """
        Build FAISS index and save both index and chunks to disk.
        
        Args:
            chunks: List of text chunks
            embeddings: List of embedding vectors
        """
        if not chunks or not embeddings:
            print("No chunks or embeddings to save")
            return
            
        # Save chunks to parquet
        chunks_df = pd.DataFrame({"text": chunks})
        chunks_df.to_parquet(self.config['chunks_parquet_path'], index=False)
        
        # Build and save FAISS index
        dimension = len(embeddings[0])
        embeddings_array = np.ascontiguousarray(np.array(embeddings).astype('float32'))
        
        index = faiss.IndexFlatL2(dimension)
        faiss.normalize_L2(embeddings_array)
        index.add(embeddings_array)
        
        faiss.write_index(index, self.config['faiss_index_path'])
        
        print(f"Index saved to: {self.config['faiss_index_path']}")
        print(f"Chunks saved to: {self.config['chunks_parquet_path']}")
    
    def run_indexing(self) -> None:
        """Run the complete indexing process."""
        print(f"Starting {self.mode.upper()} document indexing...")
        
        chunks, embeddings = self.process_documents()
        
        if not chunks:
            print(f"No documents processed for {self.mode.upper()} mode")
            return
            
        self.build_and_save_index(chunks, embeddings)
        print(f"Indexing {self.mode.upper()} completed successfully!")


def run_indexer(mode: str, chunk_size: int = None, overlap: int = None) -> None:
    """
    Convenience function to run document indexing.
    
    Args:
        mode: Mode ('hr' or 'qa')
        chunk_size: Size of text chunks in tokens
        overlap: Overlap between chunks in tokens
    """
    indexer = DocumentIndexer(mode, chunk_size, overlap)
    indexer.run_indexing()