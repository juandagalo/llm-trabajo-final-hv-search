# -*- coding: utf-8 -*-
"""
Created on Mon Sep  8 21:34:09 2025

@author: 000010478
"""



# Librerías principales
import os
import pandas as pd
import numpy as np
from openai import AzureOpenAI
import faiss
from dotenv import load_dotenv
from textManipulation import chunk_text, collect_files, extract_text_by_ext




def load_config():
    """Carga las variables de entorno y devuelve un diccionario de configuración."""
    load_dotenv()
    config = {
        'endpoint': os.getenv("ENDPOINT"),
        'deployment': os.getenv("DEPLOYMENT"),
        'api_key': os.getenv("AZURE_OPENAI_API_KEY"),
        'api_version': os.getenv("AZURE_OPENAI_API_VERSION"),
        'chunk_size': int(os.getenv("CHUNK_SIZE", 100)),
        'overlap': int(os.getenv("CHUNK_OVERLAP", 10)),
        'folder': os.getenv("CHUNKS_FOLDER", "./DocumentosPDF/"),
        'out_index': os.getenv("FAISS_INDEX_PATH", "./faiss_index.faiss"),
        'chunks_parquet': os.getenv("CHUNKS_PARQUET_PATH", "chunks.parquet")
    }
    return config

def get_azure_client(config):
    """Inicializa y retorna el cliente de Azure OpenAI."""
    return AzureOpenAI(
        api_key=config['api_key'],
        api_version=config['api_version'],
        azure_endpoint=config['endpoint']
    )

def process_documents(client, config):
    """
    Procesa los documentos de la carpeta indicada, generando los chunks y sus embeddings.
    Cada chunk lleva el nombre del candidato (extraído del nombre del archivo) al inicio.
    Devuelve dos listas: los chunks y los embeddings.
    """
    chunks = []
    embeddings = []
    for file in collect_files(config['folder']):
        # Extraer nombre del candidato del archivo (sin extensión ni carpeta)
        candidato = os.path.splitext(os.path.basename(file))[0]
        ch = chunk_text(extract_text_by_ext(file), config['chunk_size'], config['overlap'])
        # Anteponer el nombre del candidato a cada chunk
        ch = [f"El candidato {candidato} se especializa en: {chunk}" for chunk in ch]
        print(f'Documento: {file}, compuesto de {len(ch)} chunks')
        chunks.extend(ch)
        response = client.embeddings.create(
            input=ch,
            model=config['deployment']
        )
        embs = [d.embedding for d in response.data]
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


if __name__ == "__main__":
    # Carga la configuración y ejecuta el flujo principal de indexación
    config = load_config()
    client = get_azure_client(config)
    chunks, embeddings = process_documents(client, config)
    build_and_save_index(chunks, embeddings, config)
    print("Indexación completada y artefactos guardados.")


