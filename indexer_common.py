import os
import pandas as pd
import numpy as np
import faiss
from dotenv import load_dotenv
from textManipulation import chunk_text, collect_files, extract_text_by_ext
from azure_client import get_azure_client, get_embedding_deployment


def save_processed_files(filenames, output_path):
    """
    Guarda la lista de archivos procesados en un archivo de texto.
    
    Args:
        filenames: Lista de nombres de archivos procesados
        output_path: Ruta donde guardar el archivo de texto
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Archivos procesados en esta indexación\n")
            f.write(f"# Total de archivos: {len(filenames)}\n")
            f.write("# Generado automáticamente por indexer_common.py\n\n")
            
            for filename in sorted(filenames):
                f.write(f"{filename}\n")
                
        print(f"Lista de archivos procesados guardada en: {output_path}")
        
    except Exception as e:
        print(f"Error guardando lista de archivos: {e}")


def load_processed_files(filenames_path):
    """
    Carga la lista de archivos procesados desde un archivo de texto.
    
    Args:
        filenames_path: Ruta del archivo de texto con los nombres
        
    Returns:
        Lista de nombres de archivos o lista vacía si hay error
    """
    try:
        if not os.path.exists(filenames_path):
            return []
            
        with open(filenames_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Filtrar líneas que no son comentarios y no están vacías
        filenames = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                filenames.append(line)
                
        return filenames
        
    except Exception as e:
        print(f"Error cargando lista de archivos: {e}")
        return []


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
    
    # Agregar ruta para el archivo de filenames
    base_name = os.path.splitext(config['chunks_parquet'])[0]
    config['filenames_txt'] = f"{base_name}_filenames.txt"
    
    return config


def process_documents(config):
    """
    Procesa los documentos de la carpeta indicada, generando los chunks y sus embeddings.
    Cada chunk lleva el nombre del candidato (extraído del nombre del archivo) al inicio.
    Devuelve dos listas: los chunks y los embeddings, y guarda la lista de archivos procesados.
    """
    client = get_azure_client()
    deployment = get_embedding_deployment()
    
    chunks = []
    embeddings = []
    processed_files = []
    
    files_to_process = collect_files(config['folder'])
    
    for file in files_to_process:
        ch = chunk_text(extract_text_by_ext(file), config['chunk_size'], config['overlap'])
        print(f'Documento: {file}, compuesto de {len(ch)} chunks')
        chunks.extend(ch)
        
        # Guardar el nombre del archivo para el registro
        processed_files.append(os.path.basename(file))
        
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
    
    # Guardar la lista de archivos procesados
    save_processed_files(processed_files, config['filenames_txt'])
    
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