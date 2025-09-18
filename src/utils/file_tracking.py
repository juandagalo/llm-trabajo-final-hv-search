"""
File tracking utilities for managing processed files information.
"""
import os
from typing import List
from pathlib import Path


def save_processed_files(filenames: List[str], output_path: str) -> None:
    """
    Save the list of processed files to a text file.
    
    Args:
        filenames: List of processed filenames
        output_path: Path where to save the text file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Archivos procesados en esta indexación\n")
            f.write(f"# Total de archivos: {len(filenames)}\n")
            f.write("# Generado automáticamente por el sistema de indexación\n\n")
            
            for filename in sorted(filenames):
                f.write(f"{filename}\n")
                
        print(f"Lista de archivos procesados guardada en: {output_path}")
        
    except Exception as e:
        print(f"Error guardando lista de archivos: {e}")


def load_processed_files(filenames_path: str) -> List[str]:
    """
    Load the list of processed files from a text file.
    
    Args:
        filenames_path: Path to the text file with filenames
        
    Returns:
        List of filenames or empty list if error/file not found
    """
    try:
        if not os.path.exists(filenames_path):
            return []
            
        with open(filenames_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Filter out comments and empty lines
        filenames = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                filenames.append(line)
                
        return filenames
        
    except Exception as e:
        print(f"Error cargando lista de archivos: {e}")
        return []


def get_filenames_path(parquet_path: str) -> str:
    """
    Generate the filenames tracking file path from a parquet path.
    
    Args:
        parquet_path: Path to the parquet file
        
    Returns:
        Path to the corresponding filenames tracking file
    """
    base_path = Path(parquet_path).with_suffix("")
    return str(base_path) + "_filenames.txt"