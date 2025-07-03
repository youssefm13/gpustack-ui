"""
Unit tests for file processing service.
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from io import BytesIO

from services.file_processor import EnhancedFileProcessor, file_processor
from fastapi import UploadFile


class TestFileProcessor:
    """Test cases for FileProcessor."""

    def test_init(self):
        """Test EnhancedFileProcessor initialization."""
        processor = EnhancedFileProcessor()
        
        assert processor.max_content_length == 12000
        assert processor.max_summary_length == 2000

    def test_looks_like_header_detection(self):
        """Test header detection functionality."""
        processor = EnhancedFileProcessor()
        
        # Test various header patterns
        assert processor._looks_like_header("1. Introduction") is True
        assert processor._looks_like_header("CHAPTER ONE") is True
        assert processor._looks_like_header("# Header") is True
        assert processor._looks_like_header("Summary:") is True
        assert processor._looks_like_header("regular text") is False

    def test_determine_header_level(self):
        """Test header level determination."""
        processor = EnhancedFileProcessor()
        
        assert processor._determine_header_level("# Header") == 1
        assert processor._determine_header_level("## Header") == 2
        assert processor._determine_header_level("### Header") == 3
        assert processor._determine_header_level("CAPS HEADER") == 1
        assert processor._determine_header_level("Regular header") == 2

    def test_extract_heading_level(self):
        """Test heading level extraction from Word styles."""
        processor = EnhancedFileProcessor()
        
        assert processor._extract_heading_level("Heading 1") == 1
        assert processor._extract_heading_level("Heading 2") == 2
        assert processor._extract_heading_level("Title") == 1
        assert processor._extract_heading_level("Normal") == 2

    def test_create_metadata_summary(self):
        """Test metadata summary creation."""
        processor = EnhancedFileProcessor()
        
        metadata = {"page_count": 5, "word_count": 1000, "title": "Test Doc"}
        structure = {"headers": [{}, {}], "tables": [{}]}
        
        summary = processor._create_metadata_summary(metadata, structure)
        
        assert "5 pages" in summary
        assert "1000 words" in summary
        assert "Title: Test Doc" in summary
        assert "2 sections" in summary
        assert "1 tables" in summary

    def test_truncate_by_paragraphs(self):
        """Test paragraph-based truncation."""
        processor = EnhancedFileProcessor()
        
        long_text = "\n\n".join([f"Paragraph {i} content." for i in range(20)])
        truncated = processor._truncate_by_paragraphs(long_text, 100)
        
        assert len(truncated) <= 150  # Allow some margin
        assert "Paragraph 1" in truncated
        
    def test_extract_headers_from_text(self):
        """Test header extraction from text."""
        processor = EnhancedFileProcessor()
        
        text = "1. Introduction\nSome content\nCONCLUSION\nMore content\n# Summary"
        headers = processor._extract_headers_from_text(text)
        
        assert "1. Introduction" in headers
        assert "CONCLUSION" in headers
        assert "# Summary" in headers
        
    def test_optimize_content_for_context_small(self):
        """Test content optimization for small content."""
        processor = EnhancedFileProcessor()
        
        small_content = "This is a small document."
        optimized = processor._optimize_content_for_context(small_content, {}, {})
        
        assert optimized == small_content
        
    def test_optimize_content_for_context_large(self):
        """Test content optimization for large content."""
        processor = EnhancedFileProcessor()
        
        # Create content larger than max_content_length
        large_content = " ".join(["word"] * 3000)
        metadata = {"word_count": 3000}
        structure = {}
        
        optimized = processor._optimize_content_for_context(large_content, structure, metadata)
        
        assert len(optimized) <= processor.max_content_length + 500  # Allow some margin
        assert "3000 words" in optimized
        
    @pytest.mark.asyncio
    async def test_process_text_file(self):
        """Test processing of a text file."""
        from io import StringIO
        
        processor = EnhancedFileProcessor()
        
        # Create mock UploadFile
        content = "This is a test document.\n\nIt has multiple paragraphs."
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.txt"
        mock_file.content_type = "text/plain"
        mock_file.read.return_value = content.encode('utf-8')
        
        result = await processor._process_text(mock_file)
        
        assert "content" in result
        assert "metadata" in result
        assert "structure" in result
        assert result["content"] == content
        # Count words in the content: "This is a test document. It has multiple paragraphs."
        expected_word_count = len(content.split())
        assert result["metadata"]["word_count"] == expected_word_count
        
    def test_sandwich_truncation(self):
        """Test sandwich approach for truncation."""
        processor = EnhancedFileProcessor()
        
        # Create content with clear beginning, middle, and end
        content = "Beginning content. " * 100 + "Middle content. " * 100 + "End content. " * 100
        
        truncated = processor._truncate_with_sandwich_approach(content, 200)
        
        assert "Beginning content" in truncated
        assert "End content" in truncated
        assert "middle sections omitted" in truncated.lower()
        assert len(truncated) <= 400  # Allow some margin
