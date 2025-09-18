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
    """Extrae el texto de todas las páginas de un PDF con múltiples estrategias."""
    try:
        reader = PdfReader(path)
        texts = []
        
        for page_num, page in enumerate(reader.pages):
            try:
                # Estrategia 1: Extracción normal
                text = page.extract_text()
                
                # Estrategia 2: Si no hay texto o es muy poco, intentar con diferentes parámetros
                if not text or len(text.strip()) < 10:
                    # Intentar con extraction_mode
                    try:
                        text = page.extract_text(extraction_mode="layout")
                    except:
                        pass
                
                # Estrategia 3: Si aún no hay texto, intentar extraer por visitador
                if not text or len(text.strip()) < 10:
                    try:
                        from pypdf.generic import TextStringObject
                        
                        def visitor_body(text, cm, tm, fontDict, fontSize):
                            if isinstance(text, TextStringObject):
                                return text
                            return ""
                        
                        text = page.extract_text(visitor_text=visitor_body)
                    except:
                        pass
                
                # Si el texto sigue siendo muy poco, reportar
                if not text or len(text.strip()) < 5:
                    print(f"[read_pdf] Advertencia: Página {page_num + 1} tiene muy poco texto extraído")
                    text = text or ""
                
                texts.append(text)
                
            except Exception as page_error:
                print(f"[read_pdf] Error procesando página {page_num + 1}: {page_error}")
                texts.append("")
        
        full_text = "\n".join(texts)
        
        # Diagnóstico
        if len(full_text.strip()) < 50:
            print(f"[read_pdf] Advertencia: El PDF {path} produjo muy poco texto ({len(full_text)} caracteres)")
            print(f"[read_pdf] Esto puede indicar que el PDF contiene imágenes en lugar de texto seleccionable")
            print(f"[read_pdf] Contenido extraído: {repr(full_text[:200])}")
        
        return full_text
        
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
    
    