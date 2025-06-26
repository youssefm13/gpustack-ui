import pdfplumber
from docx import Document
from PIL import Image
import io
import re
from typing import Dict, Any, Optional, List
from fastapi import UploadFile
from datetime import datetime

class EnhancedFileProcessor:
    """
    Enhanced file processor with intelligent content extraction,
    structure preservation, and context optimization.
    """
    
    def __init__(self):
        self.max_content_length = 4000  # Increased from 1500
        self.max_summary_length = 1000
    
    async def process_file(self, file: UploadFile) -> Dict[str, Any]:
        """Process file with enhanced capabilities and return structured data."""
        
        # Extract basic file info
        file_info = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file.size if hasattr(file, 'size') else None,
            "processed_at": datetime.now().isoformat()
        }
        
        # Process content based on file type
        if file.content_type == "application/pdf":
            result = await self._process_pdf(file)
        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            result = await self._process_docx(file)
        elif file.content_type.startswith("image/"):
            result = await self._process_image(file)
        elif file.content_type.startswith("text/") or file.content_type == "text/plain":
            result = await self._process_text(file)
        else:
            # Try to process as text
            try:
                result = await self._process_text(file)
            except UnicodeDecodeError:
                result = {
                    "content": f"[Unsupported file type: {file.content_type}]",
                    "metadata": {"error": "Unsupported file type"},
                    "structure": {}
                }
        
        # Combine file info with processing results
        return {
            **file_info,
            **result,
            "optimized_content": self._optimize_content_for_context(
                result.get("content", ""),
                result.get("structure", {}),
                result.get("metadata", {})
            )
        }
    
    async def _process_pdf(self, file: UploadFile) -> Dict[str, Any]:
        """Enhanced PDF processing with structure extraction."""
        content = ""
        structure = {"pages": [], "tables": [], "headers": []}
        metadata = {}
        
        try:
            with pdfplumber.open(file.file) as pdf:
                metadata["page_count"] = len(pdf.pages)
                
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    content += f"\n--- Page {i+1} ---\n{page_text}"
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        for j, table in enumerate(tables):
                            structure["tables"].append({
                                "page": i+1,
                                "table_id": j+1,
                                "rows": len(table),
                                "cols": len(table[0]) if table else 0
                            })
                    
                    # Identify potential headers (larger text, bold, etc.)
                    headers = self._extract_headers_from_text(page_text)
                    structure["headers"].extend([
                        {"page": i+1, "text": h, "level": self._determine_header_level(h)}
                        for h in headers
                    ])
                    
                    structure["pages"].append({
                        "page": i+1,
                        "text_length": len(page_text),
                        "has_tables": bool(tables)
                    })
        
        except Exception as e:
            content = f"[Error processing PDF: {str(e)}]"
            metadata["error"] = str(e)
        
        return {
            "content": content,
            "metadata": metadata,
            "structure": structure
        }
    
    async def _process_docx(self, file: UploadFile) -> Dict[str, Any]:
        """Enhanced DOCX processing with structure extraction."""
        content = ""
        structure = {"paragraphs": [], "headers": [], "styles": []}
        metadata = {}
        
        try:
            doc = Document(file.file)
            
            # Extract core properties if available
            if hasattr(doc, 'core_properties'):
                core_props = doc.core_properties
                metadata.update({
                    "title": getattr(core_props, 'title', None),
                    "author": getattr(core_props, 'author', None),
                    "created": getattr(core_props, 'created', None),
                    "modified": getattr(core_props, 'modified', None)
                })
            
            # Process paragraphs with style information
            for i, paragraph in enumerate(doc.paragraphs):
                text = paragraph.text.strip()
                if text:
                    style_name = paragraph.style.name if paragraph.style else "Normal"
                    
                    # Identify headers by style
                    if "Heading" in style_name or style_name.startswith("Title"):
                        level = self._extract_heading_level(style_name)
                        structure["headers"].append({
                            "text": text,
                            "level": level,
                            "style": style_name,
                            "paragraph": i
                        })
                        content += f"\n{'#' * level} {text}\n"
                    else:
                        content += f"{text}\n"
                    
                    structure["paragraphs"].append({
                        "index": i,
                        "style": style_name,
                        "length": len(text),
                        "is_header": "Heading" in style_name
                    })
            
            metadata["paragraph_count"] = len(doc.paragraphs)
            
        except Exception as e:
            content = f"[Error processing DOCX: {str(e)}]"
            metadata["error"] = str(e)
        
        return {
            "content": content,
            "metadata": metadata,
            "structure": structure
        }
    
    async def _process_image(self, file: UploadFile) -> Dict[str, Any]:
        """Enhanced image processing with metadata extraction."""
        content = ""
        metadata = {}
        structure = {}
        
        try:
            file_content = await file.read()
            img = Image.open(io.BytesIO(file_content))
            
            # Extract image metadata
            metadata.update({
                "dimensions": img.size,
                "format": img.format,
                "mode": img.mode,
                "file_size_bytes": len(file_content)
            })
            
            # Get EXIF data if available
            if hasattr(img, '_getexif') and img._getexif():
                exif_data = img._getexif()
                if exif_data:
                    metadata["exif_available"] = True
                    # Extract some useful EXIF data
                    for tag_id, value in exif_data.items():
                        if tag_id in [271, 272, 306]:  # Make, Model, DateTime
                            metadata[f"exif_tag_{tag_id}"] = str(value)
            
            # TODO: Add OCR capability here in Phase 2
            content = f"""[Image Analysis]
Filename: {file.filename}
Dimensions: {img.size[0]}x{img.size[1]} pixels
Format: {img.format}
Color Mode: {img.mode}
File Size: {len(file_content):,} bytes

Note: OCR text extraction will be available in the next update."""
            
        except Exception as e:
            content = f"[Error processing image: {str(e)}]"
            metadata["error"] = str(e)
        
        return {
            "content": content,
            "metadata": metadata,
            "structure": structure
        }
    
    async def _process_text(self, file: UploadFile) -> Dict[str, Any]:
        """Enhanced text processing with structure analysis."""
        content = ""
        metadata = {}
        structure = {"lines": [], "sections": []}
        
        try:
            file_content = await file.read()
            content = file_content.decode("utf-8")
            
            lines = content.split('\n')
            metadata.update({
                "line_count": len(lines),
                "character_count": len(content),
                "word_count": len(content.split())
            })
            
            # Analyze structure
            for i, line in enumerate(lines):
                line_info = {
                    "line_number": i + 1,
                    "length": len(line),
                    "is_empty": not line.strip()
                }
                
                # Detect potential headers/sections
                if line.strip():
                    if line.isupper() or line.startswith('#') or self._looks_like_header(line):
                        line_info["is_header"] = True
                        structure["sections"].append({
                            "title": line.strip(),
                            "line": i + 1
                        })
                
                structure["lines"].append(line_info)
            
        except UnicodeDecodeError as e:
            content = f"[Error: Unable to decode text file - {str(e)}]"
            metadata["error"] = "encoding_error"
        except Exception as e:
            content = f"[Error processing text file: {str(e)}]"
            metadata["error"] = str(e)
        
        return {
            "content": content,
            "metadata": metadata,
            "structure": structure
        }
    
    def _optimize_content_for_context(self, content: str, structure: Dict, metadata: Dict) -> str:
        """Optimize content for AI context with intelligent truncation."""
        if not content or len(content) <= self.max_content_length:
            return content
        
        # Create optimized version with metadata summary
        optimization_summary = self._create_metadata_summary(metadata, structure)
        
        # Calculate available space for content
        available_space = self.max_content_length - len(optimization_summary) - 100
        
        if available_space <= 0:
            return optimization_summary + "\n[Content too large to include]"
        
        # Smart truncation - prioritize important sections
        optimized_content = self._smart_truncate(content, available_space, structure)
        
        return f"{optimization_summary}\n\n{optimized_content}"
    
    def _create_metadata_summary(self, metadata: Dict, structure: Dict) -> str:
        """Create a concise metadata summary."""
        summary_parts = []
        
        if metadata.get("page_count"):
            summary_parts.append(f"{metadata['page_count']} pages")
        if metadata.get("word_count"):
            summary_parts.append(f"{metadata['word_count']} words")
        if metadata.get("title"):
            summary_parts.append(f"Title: {metadata['title']}")
        if metadata.get("author"):
            summary_parts.append(f"Author: {metadata['author']}")
        
        # Structure info
        if structure.get("headers"):
            header_count = len(structure["headers"])
            summary_parts.append(f"{header_count} sections")
        if structure.get("tables"):
            table_count = len(structure["tables"])
            summary_parts.append(f"{table_count} tables")
        
        return f"[Document: {', '.join(summary_parts)}]" if summary_parts else "[Document processed]"
    
    def _smart_truncate(self, content: str, max_length: int, structure: Dict) -> str:
        """Intelligently truncate content preserving important sections."""
        if len(content) <= max_length:
            return content
        
        # If we have headers, try to include complete sections
        headers = structure.get("headers", [])
        if headers:
            return self._truncate_by_sections(content, max_length, headers)
        
        # Fallback to smart paragraph truncation
        return self._truncate_by_paragraphs(content, max_length)
    
    def _truncate_by_sections(self, content: str, max_length: int, headers: List[Dict]) -> str:
        """Truncate content by preserving complete sections."""
        # Try to fit the first few complete sections
        sections = content.split('\n')
        result = []
        current_length = 0
        
        for line in sections[:50]:  # Limit to first 50 lines for efficiency
            if current_length + len(line) + 1 > max_length:
                break
            result.append(line)
            current_length += len(line) + 1
        
        if current_length < len(content):
            result.append("\n[Content truncated - key sections preserved]")
        
        return '\n'.join(result)
    
    def _truncate_by_paragraphs(self, content: str, max_length: int) -> str:
        """Truncate content by preserving complete paragraphs."""
        paragraphs = content.split('\n\n')
        result = []
        current_length = 0
        
        for para in paragraphs:
            if current_length + len(para) + 2 > max_length:
                break
            result.append(para)
            current_length += len(para) + 2
        
        if current_length < len(content):
            result.append("\n[Content truncated - complete paragraphs preserved]")
        
        return '\n\n'.join(result)
    
    def _extract_headers_from_text(self, text: str) -> List[str]:
        """Extract potential headers from text using heuristics."""
        lines = text.split('\n')
        headers = []
        
        for line in lines:
            line = line.strip()
            if line and (line.isupper() or self._looks_like_header(line)):
                headers.append(line)
        
        return headers
    
    def _looks_like_header(self, line: str) -> bool:
        """Determine if a line looks like a header using heuristics."""
        line = line.strip()
        if not line:
            return False
        
        # Check for common header patterns
        header_patterns = [
            r'^\d+\.\s+[A-Z]',  # "1. Introduction"
            r'^[A-Z][A-Z\s]+$',  # All caps
            r'^#+\s',  # Markdown headers
            r'^[A-Z][^.]*:$',  # Ends with colon
        ]
        
        return any(re.match(pattern, line) for pattern in header_patterns)
    
    def _determine_header_level(self, header: str) -> int:
        """Determine header level based on formatting."""
        if header.startswith('###'):
            return 3
        elif header.startswith('##'):
            return 2
        elif header.startswith('#'):
            return 1
        elif header.isupper():
            return 1
        else:
            return 2
    
    def _extract_heading_level(self, style_name: str) -> int:
        """Extract heading level from Word style name."""
        if "Heading" in style_name:
            try:
                return int(re.search(r'\d+', style_name).group())
            except (AttributeError, ValueError):
                return 1
        elif style_name.startswith("Title"):
            return 1
        else:
            return 2

# Create global instance
file_processor = EnhancedFileProcessor()

# Maintain backward compatibility
async def process_file(file: UploadFile):
    """Backward compatible function that returns just content."""
    result = await file_processor.process_file(file)
    return result.get("optimized_content", result.get("content", ""))

