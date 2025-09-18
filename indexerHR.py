from indexer_common import run_indexer

if __name__ == "__main__":
    # Ejecuta el flujo de indexación para documentos HR
    run_indexer(
        default_folder="./DocumentosHR/",
        default_index_path="./faiss_index_hr.faiss",
        default_chunks_path="chunks_hr.parquet",
        indexer_type="HR",
        chunk_size=200,
        overlap=20
    )