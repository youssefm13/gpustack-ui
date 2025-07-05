from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from typing import Annotated, List, Optional
from services.file_processor import file_processor, process_file
from services.ai_document_processor import ai_document_processor, DocumentAnalysisMode
from middleware.auth_enhanced import get_current_user
from models.user import User
import logging
from api.schemas import FileUploadResponse, LegacyFileUploadResponse, ErrorResponse, BatchFileUploadResponse
import asyncio
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=FileUploadResponse, responses={413: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def upload_file(
    file: UploadFile = File(...),
    analysis_mode: Optional[str] = Form("quick"),
    current_user: Annotated[User, Depends(get_current_user)] = None
) -> FileUploadResponse:
    """
    Upload and process documents with AI-optimized content extraction.
    
    This endpoint accepts various file formats and processes them to extract content
    optimized for AI consumption. It provides detailed metadata and structural information.
    
    **Supported formats:**
    - PDF files (*.pdf)
    - Text files (*.txt)
    - Microsoft Word documents (*.docx)
    - Images with OCR (*.jpg, *.png, *.jpeg, *.gif, *.tiff, *.bmp)
    - Other text-based formats
    
    **Analysis Modes:**
    - `quick`: Fast analysis for real-time use (default)
    - `detailed`: Comprehensive analysis with detailed insights
    - `semantic`: Deep semantic understanding
    - `structured`: Focus on document structure
    
    **Features:**
    - Intelligent content chunking and optimization
    - Metadata extraction (page count, word count, file size)
    - Structure analysis (headers, tables, formatting)
    - AI-powered document insights
    - Semantic chunking for better context management
    - Content truncation with context preservation
    
    **Limits:**
    - Maximum file size: 50MB
    - Maximum content length: Optimized for AI context windows
    
    Returns detailed processing information including extracted content,
    metadata, structure analysis, AI insights, and processing notes.
    """
    try:
        # Check file size (limit to 50MB)
        if hasattr(file, 'size') and file.size and file.size > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")
        
        # Determine analysis mode
        try:
            mode = DocumentAnalysisMode(analysis_mode)
        except ValueError:
            mode = DocumentAnalysisMode.QUICK
        
        # Process file with enhanced capabilities
        result = await file_processor.process_file(file)
        
        # Apply AI-powered analysis
        enhanced_result = await ai_document_processor.enhance_document_processing(result, mode)
        
        # Log processing results for debugging
        logger.info(f"Processed file: {enhanced_result.get('filename')} ({enhanced_result.get('content_type')}) with {mode.value} analysis")
        
        # Extract AI insights
        ai_insights = enhanced_result.get("ai_insights")
        
        # Return comprehensive result
        return {
            "content": enhanced_result.get("enhanced_content", enhanced_result.get("content", "")),
            "filename": enhanced_result.get("filename"),
            "content_type": enhanced_result.get("content_type"),
            "metadata": enhanced_result.get("metadata", {}),
            "structure_info": {
                "has_headers": bool(enhanced_result.get("structure", {}).get("headers")),
                "has_tables": bool(enhanced_result.get("structure", {}).get("tables")),
                "page_count": enhanced_result.get("metadata", {}).get("page_count"),
                "word_count": enhanced_result.get("metadata", {}).get("word_count")
            },
            "ai_insights": {
                "summary": ai_insights.summary if ai_insights else "",
                "key_points": ai_insights.key_points if ai_insights else [],
                "topics": ai_insights.topics if ai_insights else [],
                "sentiment": ai_insights.sentiment if ai_insights else "neutral",
                "complexity_score": ai_insights.complexity_score if ai_insights else 0.5,
                "reading_time_minutes": ai_insights.reading_time_minutes if ai_insights else 5,
                "target_audience": ai_insights.target_audience if ai_insights else "general",
                "document_type": ai_insights.document_type if ai_insights else "document",
                "confidence_score": ai_insights.confidence_score if ai_insights else 0.8
            },
            "semantic_chunks": [
                {
                    "content": chunk.content,
                    "topic": chunk.topic,
                    "importance_score": chunk.importance_score,
                    "context": chunk.context
                }
                for chunk in enhanced_result.get("semantic_chunks", [])
            ],
            "processing_status": "success" if not enhanced_result.get("metadata", {}).get("error") else "error",
            "processing_notes": enhanced_result.get("processing_notes", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/upload/batch", response_model=BatchFileUploadResponse, responses={413: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def upload_files_batch(
    files: List[UploadFile] = File(...),
    analysis_mode: Optional[str] = Form("quick"),
    current_user: Annotated[User, Depends(get_current_user)] = None
) -> BatchFileUploadResponse:
    """
    Upload and process multiple documents with batch processing capabilities.
    
    This endpoint accepts multiple files and processes them in parallel with AI-powered analysis.
    Ideal for processing large document collections efficiently.
    
    **Features:**
    - Parallel processing of multiple files
    - Batch AI analysis with consistent analysis mode
    - Cross-document insights and relationships
    - Batch metadata and structure analysis
    - Progress tracking and error handling
    
    **Limits:**
    - Maximum 10 files per batch
    - Maximum 50MB per file
    - Total batch size: 200MB
    
    Returns batch processing results with individual file results and batch insights.
    """
    try:
        # Validate batch size
        if len(files) > 10:
            raise HTTPException(status_code=413, detail="Too many files. Maximum 10 files per batch.")
        
        # Check total batch size
        total_size = sum(file.size for file in files if hasattr(file, 'size') and file.size)
        if total_size > 200 * 1024 * 1024:  # 200MB total limit
            raise HTTPException(status_code=413, detail="Batch too large. Maximum 200MB total.")
        
        # Determine analysis mode
        try:
            mode = DocumentAnalysisMode(analysis_mode)
        except ValueError:
            mode = DocumentAnalysisMode.QUICK
        
        # Process files in parallel
        processing_tasks = []
        for file in files:
            task = asyncio.create_task(process_single_file(file, mode))
            processing_tasks.append(task)
        
        # Wait for all files to be processed
        results = await asyncio.gather(*processing_tasks, return_exceptions=True)
        
        # Process results and handle errors
        successful_results = []
        failed_files = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_files.append({
                    "filename": files[i].filename,
                    "error": str(result)
                })
            else:
                successful_results.append(result)
        
        # Generate batch insights if we have successful results
        batch_insights = None
        if successful_results:
            batch_insights = await generate_batch_insights(successful_results)
        
        return {
            "batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "total_files": len(files),
            "successful_files": len(successful_results),
            "failed_files": len(failed_files),
            "analysis_mode": mode.value,
            "results": successful_results,
            "failed_files": failed_files,
            "batch_insights": batch_insights,
            "processing_time": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing batch upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing batch upload: {str(e)}")

@router.post("/upload/legacy", response_model=LegacyFileUploadResponse, responses={500: {"model": ErrorResponse}})
async def upload_file_legacy(
    file: UploadFile = File(...),
    current_user: Annotated[User, Depends(get_current_user)] = None
) -> LegacyFileUploadResponse:
    """
    Legacy file upload endpoint for backward compatibility.
    
    This endpoint provides the original simple file upload functionality
    without enhanced metadata and structure analysis.
    
    Returns only the extracted text content from the uploaded file.
    """
    content = await process_file(file)
    return {"content": content}

async def process_single_file(file: UploadFile, mode: DocumentAnalysisMode) -> dict:
    """Process a single file with error handling."""
    try:
        # Check file size
        if hasattr(file, 'size') and file.size and file.size > 50 * 1024 * 1024:
            raise ValueError("File too large. Maximum size is 50MB.")
        
        # Process file
        result = await file_processor.process_file(file)
        
        # Apply AI analysis
        enhanced_result = await ai_document_processor.enhance_document_processing(result, mode)
        
        # Extract AI insights
        ai_insights = enhanced_result.get("ai_insights")
        
        return {
            "content": enhanced_result.get("enhanced_content", enhanced_result.get("content", "")),
            "filename": enhanced_result.get("filename"),
            "content_type": enhanced_result.get("content_type"),
            "metadata": enhanced_result.get("metadata", {}),
            "structure_info": {
                "has_headers": bool(enhanced_result.get("structure", {}).get("headers")),
                "has_tables": bool(enhanced_result.get("structure", {}).get("tables")),
                "page_count": enhanced_result.get("metadata", {}).get("page_count"),
                "word_count": enhanced_result.get("metadata", {}).get("word_count")
            },
            "ai_insights": {
                "summary": ai_insights.summary if ai_insights else "",
                "key_points": ai_insights.key_points if ai_insights else [],
                "topics": ai_insights.topics if ai_insights else [],
                "sentiment": ai_insights.sentiment if ai_insights else "neutral",
                "complexity_score": ai_insights.complexity_score if ai_insights else 0.5,
                "reading_time_minutes": ai_insights.reading_time_minutes if ai_insights else 5,
                "target_audience": ai_insights.target_audience if ai_insights else "general",
                "document_type": ai_insights.document_type if ai_insights else "document",
                "confidence_score": ai_insights.confidence_score if ai_insights else 0.8
            },
            "semantic_chunks": [
                {
                    "content": chunk.content,
                    "topic": chunk.topic,
                    "importance_score": chunk.importance_score,
                    "context": chunk.context
                }
                for chunk in enhanced_result.get("semantic_chunks", [])
            ],
            "processing_status": "success" if not enhanced_result.get("metadata", {}).get("error") else "error",
            "processing_notes": enhanced_result.get("processing_notes", [])
        }
        
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        raise e

async def generate_batch_insights(results: List[dict]) -> dict:
    """Generate insights across multiple documents."""
    try:
        # Collect all content and insights
        all_content = []
        all_topics = []
        all_key_points = []
        
        for result in results:
            content = result.get("content", "")
            if content:
                all_content.append(content[:1000])  # Limit each file's contribution
            
            ai_insights = result.get("ai_insights", {})
            if ai_insights.get("topics"):
                all_topics.extend(ai_insights["topics"])
            if ai_insights.get("key_points"):
                all_key_points.extend(ai_insights["key_points"])
        
        # Create batch summary
        combined_content = "\n\n".join(all_content[:5])  # Limit to first 5 files
        
        batch_prompt = f"""
        Analyze this batch of documents and provide insights:

        {combined_content}

        Topics found: {list(set(all_topics))}
        Key points: {all_key_points[:10]}

        Provide JSON response with:
        - batch_summary: Summary of the document collection
        - common_themes: Themes across all documents
        - document_relationships: How documents relate to each other
        - total_insights: Key insights from the batch
        """
        
        # This would require the inference client to be available
        # For now, return a simple batch insight
        return {
            "batch_summary": f"Processed {len(results)} documents successfully",
            "common_themes": list(set(all_topics)),
            "document_relationships": "Documents processed independently",
            "total_insights": all_key_points[:10]
        }
        
    except Exception as e:
        logger.error(f"Error generating batch insights: {str(e)}")
        return {
            "batch_summary": f"Processed {len(results)} documents",
            "common_themes": [],
            "document_relationships": "Analysis unavailable",
            "total_insights": []
        }
