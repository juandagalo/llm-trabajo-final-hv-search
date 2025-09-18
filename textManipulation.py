from typing import List
from pathlib import Path
import glob
import tiktoken
from pypdf import PdfReader

def read_txt(path: str) -> str:
    """Lee el contenido de un archivo de texto plano."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"[read_txt] Error leyendo {path}: {e}")
        return ""

def read_pdf(path: str) -> str:
    """Extrae el texto de todas las páginas de un PDF."""
    try:
        reader = PdfReader(path)
        texts = []
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                texts.append("")
        return "\n".join(texts)
    except Exception as e:
        print(f"[read_pdf] Error leyendo {path}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int, overlap: int, model_name: str = "text-embedding-3-small") -> List[str]:
    """
    Divide un texto en chunks de tamaño chunk_size (en tokens), con solapamiento.
    Args:
        text: Texto a dividir.
        chunk_size: Tamaño de chunk en tokens.
        overlap: Número de tokens de solapamiento entre chunks.
        model_name: Modelo para tiktoken.
    Returns:
        List[str]: Lista de chunks de texto.
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
    Busca archivos con extensiones dadas en un directorio (recursivo).
    Args:
        input_dir: Directorio raíz.
        extensions: Lista de extensiones (ej: ['pdf', 'txt']). Si None, busca pdf y txt.
    Returns:
        Lista de rutas absolutas de archivos encontrados.
    """
    if extensions is None:
        extensions = ["pdf", "txt"]
    files = []
    for ext in extensions:
        files.extend(glob.glob(str(Path(input_dir) / f"**/*.{ext}"), recursive=True))
    # Quitar duplicados y ordenar
    files = sorted(set(files))
    return files

def extract_text_by_ext(path: str) -> str:
    """
    Extrae el texto de un archivo según su extensión.
    Args:
        path: Ruta del archivo.
    Returns:
        Texto extraído o vacío si no es compatible.
    """
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return read_pdf(path)
    elif ext in [".txt", ".md"]:
        return read_txt(path)
    else:
        print(f"[extract_text_by_ext] Extensión no soportada: {ext} ({path})")
        return ""
    
    