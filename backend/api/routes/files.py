from fastapi import APIRouter, UploadFile, File, HTTPException
from services.file_processor import file_processor, process_file
import logging
from api.schemas import FileUploadResponse, LegacyFileUploadResponse, ErrorResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=FileUploadResponse, responses={413: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def upload_file(file: UploadFile = File(...)) -> FileUploadResponse:
    """
    Upload and process documents with AI-optimized content extraction.
    
    This endpoint accepts various file formats and processes them to extract content
    optimized for AI consumption. It provides detailed metadata and structural information.
    
    **Supported formats:**
    - PDF files (*.pdf)
    - Text files (*.txt)
    - Microsoft Word documents (*.docx)
    - Other text-based formats
    
    **Features:**
    - Intelligent content chunking and optimization
    - Metadata extraction (page count, word count, file size)
    - Structure analysis (headers, tables, formatting)
    - Content truncation with context preservation
    
    **Limits:**
    - Maximum file size: 50MB
    - Maximum content length: Optimized for AI context windows
    
    Returns detailed processing information including extracted content,
    metadata, structure analysis, and processing notes.
    """
    try:
        # Check file size (limit to 50MB)
        if hasattr(file, 'size') and file.size and file.size > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")
        
        # Process file with enhanced capabilities
        result = await file_processor.process_file(file)
        
        # Log processing results for debugging
        logger.info(f"Processed file: {result.get('filename')} ({result.get('content_type')})")
        
        # Return comprehensive result
        return {
            "content": result.get("optimized_content", result.get("content", "")),
            "filename": result.get("filename"),
            "content_type": result.get("content_type"),
            "metadata": result.get("metadata", {}),
            "structure_info": {
                "has_headers": bool(result.get("structure", {}).get("headers")),
                "has_tables": bool(result.get("structure", {}).get("tables")),
                "page_count": result.get("metadata", {}).get("page_count"),
                "word_count": result.get("metadata", {}).get("word_count")
            },
            "processing_status": "success" if not result.get("metadata", {}).get("error") else "error",
            "processing_notes": [
                f"Content optimized for AI context (max {file_processor.max_content_length} chars)",
                "Structure and metadata preserved",
                "Intelligent truncation applied if needed"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/upload/legacy", response_model=LegacyFileUploadResponse, responses={500: {"model": ErrorResponse}})
async def upload_file_legacy(file: UploadFile = File(...)) -> LegacyFileUploadResponse:
    """
    Legacy file upload endpoint for backward compatibility.
    
    This endpoint provides the original simple file upload functionality
    without enhanced metadata and structure analysis.
    
    Returns only the extracted text content from the uploaded file.
    """
    content = await process_file(file)
    return {"content": content}
