"""
Unit tests for file processing service.
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from io import BytesIO

from services.file_processor import EnhancedFileProcessor


class TestFileProcessor:
    """Test cases for FileProcessor."""

    def test_init(self):
        """Test FileProcessor initialization."""
        processor = FileProcessor()
        
        assert processor.max_file_size_mb == 50
        assert processor.max_words == 5000

    def test_get_file_type_pdf(self):
        """Test file type detection for PDF."""
        processor = FileProcessor()
        
        file_type = processor.get_file_type("document.pdf")
        
        assert file_type == "pdf"

    def test_get_file_type_docx(self):
        """Test file type detection for DOCX."""
        processor = FileProcessor()
        
        file_type = processor.get_file_type("document.docx")
        
        assert file_type == "docx"

    def test_get_file_type_txt(self):
        """Test file type detection for text files."""
        processor = FileProcessor()
        
        file_type = processor.get_file_type("document.txt")
        
        assert file_type == "txt"

    def test_get_file_type_unsupported(self):
        """Test file type detection for unsupported files."""
        processor = FileProcessor()
        
        file_type = processor.get_file_type("document.xyz")
        
        assert file_type == "unsupported"

    def test_validate_file_size_valid(self):
        """Test file size validation for valid file."""
        processor = FileProcessor()
        
        # Create a small test file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"test content")
            tmp_file.flush()
            
            is_valid = processor.validate_file_size(tmp_file.name)
            
            assert is_valid is True
            
        os.unlink(tmp_file.name)

    def test_validate_file_size_too_large(self):
        """Test file size validation for oversized file."""
        processor = FileProcessor()
        
        # Mock file size to be larger than limit
        with patch('os.path.getsize') as mock_getsize:
            mock_getsize.return_value = 60 * 1024 * 1024  # 60MB
            
            is_valid = processor.validate_file_size("fake_file.pdf")
            
            assert is_valid is False

    def test_extract_text_from_txt(self):
        """Test text extraction from plain text file."""
        processor = FileProcessor()
        content = "This is a test document content."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file.flush()
            
            extracted_text = processor.extract_text_from_txt(tmp_file.name)
            
            assert extracted_text == content
            
        os.unlink(tmp_file.name)

    @patch('pdfplumber.open')
    def test_extract_text_from_pdf_success(self, mock_pdf_open):
        """Test successful text extraction from PDF."""
        processor = FileProcessor()
        
        # Mock PDF document
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PDF content"
        
        mock_pdf = MagicMock()
        mock_pdf.__enter__.return_value.pages = [mock_page]
        mock_pdf_open.return_value = mock_pdf
        
        extracted_text = processor.extract_text_from_pdf("test.pdf")
        
        assert extracted_text == "PDF content"

    @patch('pdfplumber.open')
    def test_extract_text_from_pdf_failure(self, mock_pdf_open):
        """Test PDF text extraction failure."""
        processor = FileProcessor()
        
        mock_pdf_open.side_effect = Exception("PDF error")
        
        extracted_text = processor.extract_text_from_pdf("test.pdf")
        
        assert extracted_text == ""

    @patch('docx.Document')
    def test_extract_text_from_docx_success(self, mock_document):
        """Test successful text extraction from DOCX."""
        processor = FileProcessor()
        
        # Mock DOCX document
        mock_paragraph = MagicMock()
        mock_paragraph.text = "DOCX content"
        
        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_paragraph]
        mock_document.return_value = mock_doc
        
        extracted_text = processor.extract_text_from_docx("test.docx")
        
        assert extracted_text == "DOCX content"

    @patch('docx.Document')
    def test_extract_text_from_docx_failure(self, mock_document):
        """Test DOCX text extraction failure."""
        processor = FileProcessor()
        
        mock_document.side_effect = Exception("DOCX error")
        
        extracted_text = processor.extract_text_from_docx("test.docx")
        
        assert extracted_text == ""

    def test_analyze_structure_basic(self):
        """Test basic structure analysis."""
        processor = FileProcessor()
        text = "This is a test document with multiple words."
        
        structure_info = processor.analyze_structure(text)
        
        assert structure_info["word_count"] == 8
        assert structure_info["has_headers"] is False
        assert structure_info["has_tables"] is False

    def test_analyze_structure_with_headers(self):
        """Test structure analysis with headers."""
        processor = FileProcessor()
        text = "# Header 1\nSome content\n## Header 2\nMore content"
        
        structure_info = processor.analyze_structure(text)
        
        assert structure_info["has_headers"] is True

    def test_analyze_structure_with_tables(self):
        """Test structure analysis with tables."""
        processor = FileProcessor()
        text = "Some content\n| Column 1 | Column 2 |\n|----------|----------|\n| Data 1   | Data 2   |"
        
        structure_info = processor.analyze_structure(text)
        
        assert structure_info["has_tables"] is True

    def test_clean_and_optimize_text_basic(self):
        """Test basic text cleaning and optimization."""
        processor = FileProcessor()
        text = "  This is a test   document.  \n\n  With extra   spaces.  "
        
        cleaned_text = processor.clean_and_optimize_text(text)
        
        assert "This is a test document." in cleaned_text
        assert "With extra spaces." in cleaned_text

    def test_clean_and_optimize_text_truncation(self):
        """Test text truncation for long documents."""
        processor = FileProcessor()
        long_text = " ".join(["word"] * 6000)  # More than max_words
        
        cleaned_text = processor.clean_and_optimize_text(long_text)
        
        word_count = len(cleaned_text.split())
        assert word_count <= processor.max_words

    def test_extract_metadata_basic(self):
        """Test basic metadata extraction."""
        processor = FileProcessor()
        text = "Document Title\nBy Author Name\nThis is the content."
        
        metadata = processor.extract_metadata(text, "test.txt")
        
        assert metadata["filename"] == "test.txt"
        assert metadata["content_type"] == "text/plain"

    async def test_process_file_txt_success(self):
        """Test successful processing of text file."""
        processor = FileProcessor()
        content = "This is a test document content."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file.flush()
            
            result = await processor.process_file(tmp_file.name)
            
            assert result["success"] is True
            assert result["content"] == content
            assert result["filename"] == os.path.basename(tmp_file.name)
            assert "structure_info" in result
            assert "metadata" in result
            
        os.unlink(tmp_file.name)

    async def test_process_file_unsupported(self):
        """Test processing of unsupported file type."""
        processor = FileProcessor()
        
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as tmp_file:
            tmp_file.write(b"content")
            tmp_file.flush()
            
            result = await processor.process_file(tmp_file.name)
            
            assert result["success"] is False
            assert "Unsupported file type" in result["error"]
            
        os.unlink(tmp_file.name)

    async def test_process_file_too_large(self):
        """Test processing of oversized file."""
        processor = FileProcessor()
        
        with patch.object(processor, 'validate_file_size', return_value=False):
            result = await processor.process_file("fake_large_file.txt")
            
            assert result["success"] is False
            assert "File too large" in result["error"]
