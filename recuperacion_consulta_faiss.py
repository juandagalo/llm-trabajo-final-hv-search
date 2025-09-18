# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 15:33:01 2025

@author: 000010478
"""

# query_search.py

import os
import numpy as np
import pandas as pd
import faiss
from dotenv import load_dotenv
from azure_client import get_azure_client, get_embedding_deployment, is_mock_mode


# ========= Configuración desde .env =========
load_dotenv()

# Configuración para modo HR
FAISS_INDEX_HR_PATH = os.getenv("FAISS_INDEX_HR_PATH", "./faiss_index_hr.faiss")
PARQUET_HR_PATH = os.getenv("CHUNKS_PARQUET_HR_PATH", "./chunks_hr.parquet")

# Configuración para modo QA
FAISS_INDEX_QA_PATH = os.getenv("FAISS_INDEX_QA_PATH", "./faiss_index_qa.faiss")
PARQUET_QA_PATH = os.getenv("CHUNKS_PARQUET_QA_PATH", "./chunks_qa.parquet")

def get_embedding(text: str) -> np.ndarray:
    """Obtiene el embedding de una sola frase."""
    if is_mock_mode():
        # Return a mock embedding for demo purposes
        emb = np.random.rand(1536).astype('float32')  # Common embedding size
        emb = np.ascontiguousarray(emb.reshape(1, -1))
        faiss.normalize_L2(emb)
        return emb
    
    client = get_azure_client()
    deployment = get_embedding_deployment()
        
    resp = client.embeddings.create(
        input=[text],
        model=deployment
    )
    emb = np.array(resp.data[0].embedding, dtype="float32")
    emb = np.ascontiguousarray(emb.reshape(1, -1))
    faiss.normalize_L2(emb)
    return emb

def load_artifacts(mode: str = "hr"):
    """Carga índice FAISS y el dataframe de chunks (parquet).
    mode: "hr" for Human Resources, "qa" for QA Testing - allows for different indices."""
    
    # Selecciona las rutas correctas según el modo
    if mode.lower() == "qa":
        faiss_path = FAISS_INDEX_QA_PATH
        parquet_path = PARQUET_QA_PATH
    else:  # mode == "hr" (default)
        faiss_path = FAISS_INDEX_HR_PATH
        parquet_path = PARQUET_HR_PATH
    
    if is_mock_mode():
        # Create mock data for demo purposes
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
        else:  # HR mode
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
        
        # Create a simple mock FAISS index
        d = 1536  # Common embedding dimension
        index = faiss.IndexFlatL2(d)
        mock_embeddings = np.random.rand(len(mock_data["text"]), d).astype('float32')
        faiss.normalize_L2(mock_embeddings)
        index.add(mock_embeddings)
        
        return index, df
    
    try:
        index = faiss.read_index(faiss_path)
        df = pd.read_parquet(parquet_path)
    except FileNotFoundError as e:
        available_modes = []
        if os.path.exists(FAISS_INDEX_HR_PATH) and os.path.exists(PARQUET_HR_PATH):
            available_modes.append("hr")
        if os.path.exists(FAISS_INDEX_QA_PATH) and os.path.exists(PARQUET_QA_PATH):
            available_modes.append("qa")
        
        if available_modes:
            raise FileNotFoundError(f"No se encontraron archivos para el modo '{mode}'. "
                                  f"Modos disponibles: {available_modes}. "
                                  f"Archivo faltante: {e}")
        else:
            raise FileNotFoundError(f"No se encontraron índices para ningún modo. "
                                  f"Ejecuta primero los indexadores (indexerHR.py o indexerQA.py).")
    
    # Normaliza nombres: intenta usar columna 'text' si existe; si no, usa la primera
    if "text" not in df.columns:
        if len(df.columns) == 1:
            df = df.rename(columns={df.columns[0]: "text"})
        elif "chunk" in df.columns:
            df = df.rename(columns={"chunk": "text"})
        else:
            raise ValueError("No encuentro columna de texto. Asegura que el parquet tenga una columna 'text'.")
    return index, df

def cosine_from_l2_dist(dist_sq: np.ndarray) -> np.ndarray:
    """
    Convierte distancia L2^2 entre vectores unitarios a similitud coseno.
    Para vectores normalizados:  ||a-b||^2 = 2(1 - cos_sim)  =>  cos_sim = 1 - dist^2/2
    """
    return 1.0 - dist_sq / 2.0


def check_available_modes():
    """
    Verifica qué modos están disponibles según los archivos presentes.
    
    Returns:
        dict: Diccionario con información sobre modos disponibles incluyendo archivos procesados
    """
    available_modes = {}
    
    # Configurar rutas de archivos de filenames
    hr_filenames_path = os.path.splitext(PARQUET_HR_PATH)[0] + "_filenames.txt"
    qa_filenames_path = os.path.splitext(PARQUET_QA_PATH)[0] + "_filenames.txt"
    
    # Verificar modo HR
    if os.path.exists(FAISS_INDEX_HR_PATH) and os.path.exists(PARQUET_HR_PATH):
        # Cargar lista de archivos procesados
        processed_files = load_processed_files(hr_filenames_path)
        available_modes["hr"] = {
            "available": True,
            "faiss_path": FAISS_INDEX_HR_PATH,
            "parquet_path": PARQUET_HR_PATH,
            "filenames_path": hr_filenames_path,
            "processed_files": processed_files,
            "file_count": len(processed_files),
            "description": f"Human Resources documents ({len(processed_files)} files indexed)"
        }
    else:
        available_modes["hr"] = {
            "available": False,
            "faiss_path": FAISS_INDEX_HR_PATH,
            "parquet_path": PARQUET_HR_PATH,
            "filenames_path": hr_filenames_path,
            "processed_files": [],
            "file_count": 0,
            "description": "Human Resources documents (run indexerHR.py to create)"
        }
    
    # Verificar modo QA
    if os.path.exists(FAISS_INDEX_QA_PATH) and os.path.exists(PARQUET_QA_PATH):
        # Cargar lista de archivos procesados
        processed_files = load_processed_files(qa_filenames_path)
        available_modes["qa"] = {
            "available": True,
            "faiss_path": FAISS_INDEX_QA_PATH,
            "parquet_path": PARQUET_QA_PATH,
            "filenames_path": qa_filenames_path,
            "processed_files": processed_files,
            "file_count": len(processed_files),
            "description": f"QA Testing documents ({len(processed_files)} files indexed)"
        }
    else:
        available_modes["qa"] = {
            "available": False,
            "faiss_path": FAISS_INDEX_QA_PATH,
            "parquet_path": PARQUET_QA_PATH,
            "filenames_path": qa_filenames_path,
            "processed_files": [],
            "file_count": 0,
            "description": "QA Testing documents (run indexerQA.py to create)"
        }
    
    return available_modes


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

def search(query: str, k: int = 10, mode: str = "hr"):
    print(f"Buscando en modo: {mode.upper()}")
    index, df = load_artifacts(mode)
    q = get_embedding(query)
    D, I = index.search(q, k)
    D = D[0]
    I = I[0]
    results = df.iloc[I].copy()
    results["cosine_sim"] = cosine_from_l2_dist(D)
    results["faiss_id"] = I
    results["mode"] = mode.upper()  # Agrega información del modo usado
    results = results.sort_values("cosine_sim", ascending=False).reset_index(drop=True)
    print(f"Encontrados {len(results)} resultados en índice {mode.upper()}")
    return results



