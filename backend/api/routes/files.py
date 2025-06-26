from fastapi import APIRouter, UploadFile, File, HTTPException
from services.file_processor import file_processor, process_file
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Enhanced file upload with detailed processing information."""
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

@router.post("/upload/legacy")
async def upload_file_legacy(file: UploadFile = File(...)):
    """Legacy endpoint for backward compatibility."""
    content = await process_file(file)
    return {"content": content}
