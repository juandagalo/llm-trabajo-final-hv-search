import os
import pandas as pd
import numpy as np
import faiss
from dotenv import load_dotenv
from textManipulation import chunk_text, collect_files, extract_text_by_ext
from azure_client import get_azure_client, get_embedding_deployment


def load_config(default_folder, default_index_path, default_chunks_path, chunk_size, overlap):
    """
    Carga las variables de entorno y devuelve un diccionario de configuración.
    
    Args:
        default_folder: Carpeta por defecto para los documentos
        default_index_path: Ruta por defecto para el índice FAISS
        default_chunks_path: Ruta por defecto para el archivo parquet de chunks
        chunk_size: Tamaño de cada chunk
        overlap: Superposición entre chunks
    """
    load_dotenv()
    config = {
        'chunk_size': int(os.getenv("CHUNK_SIZE", chunk_size)),
        'overlap': int(os.getenv("CHUNK_OVERLAP", overlap)),
        'folder': os.getenv("CHUNKS_FOLDER", default_folder),
        'out_index': os.getenv("FAISS_INDEX_PATH", default_index_path),
        'chunks_parquet': os.getenv("CHUNKS_PARQUET_PATH", default_chunks_path)
    }
    return config


def process_documents(config):
    """
    Procesa los documentos de la carpeta indicada, generando los chunks y sus embeddings.
    Cada chunk lleva el nombre del candidato (extraído del nombre del archivo) al inicio.
    Devuelve dos listas: los chunks y los embeddings.
    """
    client = get_azure_client()
    deployment = get_embedding_deployment()
    
    chunks = []
    embeddings = []
    for file in collect_files(config['folder']):
        ch = chunk_text(extract_text_by_ext(file), config['chunk_size'], config['overlap'])
        print(f'Documento: {file}, compuesto de {len(ch)} chunks')
        chunks.extend(ch)
        
        if client:
            response = client.embeddings.create(
                input=ch,
                model=deployment
            )
            embs = [d.embedding for d in response.data]
        else:
            # Modo mock para demo
            import numpy as np
            embs = [np.random.rand(1536).astype('float32').tolist() for _ in ch]
            print("⚠️  Usando embeddings mock (modo demo)")
        
        embeddings.extend(embs)
    return chunks, embeddings


def build_and_save_index(chunks, embeddings, config):
    """
    Construye el índice FAISS y guarda tanto el índice como los chunks en disco.
    """
    data = pd.DataFrame(data=chunks)
    d = len(embeddings[0])
    embeddings = np.ascontiguousarray(np.array(embeddings).astype('float32'))
    index = faiss.IndexFlatL2(d)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    faiss.write_index(index, str(config['out_index']))
    data.to_parquet(config['chunks_parquet'])


def run_indexer(default_folder, default_index_path, default_chunks_path, indexer_type="general", chunk_size=100, overlap=10):
    """
    Ejecuta el flujo completo de indexación.
    
    Args:
        default_folder: Carpeta por defecto para los documentos
        default_index_path: Ruta por defecto para el índice FAISS
        default_chunks_path: Ruta por defecto para el archivo parquet de chunks
        indexer_type: Tipo de indexador para los mensajes de log
        chunk_size: Tamaño de cada chunk (por defecto 100)
        overlap: Superposición entre chunks (por defecto 10)
    """
    config = load_config(default_folder, default_index_path, default_chunks_path, chunk_size, overlap)
    chunks, embeddings = process_documents(config)
    build_and_save_index(chunks, embeddings, config)
    print(f"Indexación {indexer_type} completada y artefactos guardados.")