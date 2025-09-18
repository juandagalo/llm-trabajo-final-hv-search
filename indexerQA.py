from indexer_common import run_indexer

if __name__ == "__main__":
    # Ejecuta el flujo de indexación para documentos QA
    run_indexer(
        default_folder="./DocumentosQA/",
        default_index_path="./faiss_index_qa.faiss",
        default_chunks_path="chunks_qa.parquet",
        indexer_type="QA",
        chunk_size=150,
        overlap=12
    )