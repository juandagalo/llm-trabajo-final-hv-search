# Cleanup Script for Old Files
# Run this after verifying the new structure works correctly

Write-Host "=== LLM HV Search - Cleanup Old Files ===" -ForegroundColor Yellow
Write-Host ""

# Files to remove (replaced by new modular structure)
$filesToRemove = @(
    "azure_client.py",
    "indexer_common.py", 
    "recuperacion_consulta_faiss.py",
    "RagSearch.py",
    "textManipulation.py",
    "main.py",
    "indexerHR.py", 
    "indexerQA.py",
    "faiss_index.faiss",
    "chunks.parquet",
    "faiss_index_hr.faiss",
    "chunks_hr.parquet", 
    "chunks_hr_filenames.txt",
    "faiss_index_qa.faiss",
    "chunks_qa.parquet",
    "chunks_qa_filenames.txt"
)

Write-Host "Checking files to remove:" -ForegroundColor Cyan
$foundFiles = @()

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Write-Host "  Found: $file" -ForegroundColor Green
        $foundFiles += $file
    } else {
        Write-Host "  Not found: $file" -ForegroundColor Gray
    }
}

if ($foundFiles.Count -eq 0) {
    Write-Host ""
    Write-Host "No old files found to remove." -ForegroundColor Green
    Write-Host "Cleanup already completed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Found $($foundFiles.Count) files to remove." -ForegroundColor Yellow
    Write-Host ""
    
    $confirm = Read-Host "Do you want to remove these files? (y/N)"
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Write-Host ""
        Write-Host "Removing files..." -ForegroundColor Yellow
        
        foreach ($file in $foundFiles) {
            try {
                Remove-Item $file -Force
                Write-Host "  Removed: $file" -ForegroundColor Green
            } catch {
                Write-Host "  Error removing $file" -ForegroundColor Red
            }
        }
        
        Write-Host ""
        Write-Host "Cleanup completed!" -ForegroundColor Green
        Write-Host "Your project now uses the clean modular structure." -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Cleanup cancelled. Files preserved." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== New Project Structure ===" -ForegroundColor Cyan
Write-Host "src/core/         - Core business logic"
Write-Host "src/utils/        - Utility functions"  
Write-Host "src/config/       - Configuration management"
Write-Host "data/indexes/     - All data files"
Write-Host "app.py           - Streamlit application"
Write-Host "indexer_hr.py    - HR indexer script"
Write-Host "indexer_qa.py    - QA indexer script"