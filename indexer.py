#!/usr/bin/env python
"""
Document Indexer CLI

Usage:
    python indexer.py hr          # Index HR documents
    python indexer.py qa          # Index QA documents  
    python indexer.py all         # Index both HR and QA
    python indexer.py hr --chunk-size 200 --overlap 20
"""
import sys
import argparse
from src.indexer import run_indexer


def main():
    parser = argparse.ArgumentParser(description="Index documents for LLM HV Search")
    parser.add_argument("mode", choices=["hr", "qa", "all"], 
                       help="Which documents to index: hr, qa, or all")
    parser.add_argument("--chunk-size", type=int, default=100,
                       help="Chunk size in tokens (default: 100)")
    parser.add_argument("--overlap", type=int, default=10,
                       help="Overlap between chunks in tokens (default: 10)")
    
    args = parser.parse_args()
    
    if args.mode == "all":
        run_indexer("hr", args.chunk_size, args.overlap)
        run_indexer("qa", args.chunk_size, args.overlap)
    else:
        run_indexer(args.mode, args.chunk_size, args.overlap)


if __name__ == "__main__":
    main()
