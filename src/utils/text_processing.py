"""
Text processing utilities for document handling and manipulation.
"""
from typing import List
from pathlib import Path
import glob
import tiktoken
from pypdf import PdfReader


def read_txt_file(path: str) -> str:
    """Read content from a plain text file."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"[read_txt_file] Error reading {path}: {e}")
        return ""


def read_pdf_file(path: str) -> str:
    """Extract text from all pages of a PDF file with multiple strategies."""
    try:
        reader = PdfReader(path)
        texts = []
        
        for page_num, page in enumerate(reader.pages):
            try:
                # Strategy 1: Normal extraction
                text = page.extract_text()
                
                # Strategy 2: Try different extraction modes if text is minimal
                if not text or len(text.strip()) < 10:
                    try:
                        text = page.extract_text(extraction_mode="layout")
                    except:
                        pass
                
                # If still minimal text, warn about potential image-based content
                if not text or len(text.strip()) < 5:
                    print(f"[read_pdf_file] Warning: Page {page_num + 1} has minimal extractable text")
                    text = text or ""
                
                texts.append(text)
                
            except Exception as page_error:
                print(f"[read_pdf_file] Error processing page {page_num + 1}: {page_error}")
                texts.append("")
        
        full_text = "\\n".join(texts)
        
        # Diagnostic warning for image-based PDFs
        if len(full_text.strip()) < 50:
            print(f"[read_pdf_file] Warning: PDF {path} produced minimal text ({len(full_text)} chars)")
            print(f"[read_pdf_file] This may indicate image-based content requiring OCR")
        
        return full_text
        
    except Exception as e:
        print(f"[read_pdf_file] Error reading {path}: {e}")
        return ""


def chunk_text(text: str, chunk_size: int, overlap: int, model_name: str = "text-embedding-3-small") -> List[str]:
    """
    Split text into chunks of specified size (in tokens) with overlap.
    
    Args:
        text: Text to split
        chunk_size: Chunk size in tokens
        overlap: Number of overlapping tokens between chunks
        model_name: Model name for tiktoken encoding
        
    Returns:
        List of text chunks
    """
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(text)
    chunks = []
    step = max(1, chunk_size - overlap)
    
    for start in range(0, len(tokens), step):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        if end >= len(tokens):
            break
            
    return chunks


def collect_files(input_dir: str, extensions: List[str] = None) -> List[str]:
    """
    Find files with specified extensions in a directory (recursive).
    
    Args:
        input_dir: Root directory to search
        extensions: List of file extensions (e.g., ['pdf', 'txt']). Defaults to pdf and txt.
        
    Returns:
        List of absolute file paths found
    """
    if extensions is None:
        extensions = ["pdf", "txt"]
        
    files = []
    for ext in extensions:
        pattern = str(Path(input_dir) / f"**/*.{ext}")
        files.extend(glob.glob(pattern, recursive=True))
    
    # Remove duplicates and sort
    return sorted(set(files))


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from a file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Extracted text or empty string if not supported
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    
    if ext == ".pdf":
        text = read_pdf_file(file_path)
        # Suggest alternative if text extraction is poor
        if len(text.strip()) < 100:
            print(f"[extract_text_from_file] PDF {file_path} has minimal text.")
            print(f"[extract_text_from_file] Consider OCR tools for image-based PDFs.")
        return text
    elif ext in [".txt", ".md"]:
        return read_txt_file(file_path)
    else:
        print(f"[extract_text_from_file] Unsupported extension: {ext} ({file_path})")
        return ""