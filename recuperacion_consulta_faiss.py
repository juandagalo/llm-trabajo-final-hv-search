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
from openai import AzureOpenAI
from dotenv import load_dotenv


# ========= Configuración desde .env =========
load_dotenv()
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./faiss_index.faiss")
PARQUET_PATH = os.getenv("CHUNKS_PARQUET_PATH", "./chunks.parquet")
ENDPOINT = os.getenv("ENDPOINT")
DEPLOYMENT = os.getenv("DEPLOYMENT")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# ========= Cliente Azure OpenAI =========
client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=ENDPOINT
)

def get_embedding(text: str) -> np.ndarray:
    """Obtiene el embedding de una sola frase."""
    resp = client.embeddings.create(
        input=[text],
        model=DEPLOYMENT
    )
    emb = np.array(resp.data[0].embedding, dtype="float32")
    emb = np.ascontiguousarray(emb.reshape(1, -1))
    faiss.normalize_L2(emb)
    return emb

def load_artifacts():
    """Carga índice FAISS y el dataframe de chunks (parquet)."""
    index = faiss.read_index(FAISS_INDEX_PATH)
    df = pd.read_parquet(PARQUET_PATH)
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

def search(query: str, k: int = 10):
    """Busca los k más cercanos al embedding de la consulta y devuelve un DataFrame con resultados."""
    index, df = load_artifacts()
    q = get_embedding(query)
    D, I = index.search(q, k)
    D = D[0]
    I = I[0]
    results = df.iloc[I].copy()
    results["cosine_sim"] = cosine_from_l2_dist(D)
    results["faiss_id"] = I
    results = results.sort_values("cosine_sim", ascending=False).reset_index(drop=True)
    return results



