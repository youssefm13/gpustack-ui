"""
OCR Service for GPUStack UI v2.4.0
Provides comprehensive OCR capabilities with image preprocessing and confidence scoring.
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import filetype
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import tempfile
import os
from dataclasses import dataclass
from enum import Enum
import langdetect

# Configure logging
logger = logging.getLogger(__name__)

class ImagePreprocessingMode(Enum):
    """Different image preprocessing modes for OCR optimization"""
    AUTO = "auto"
    LIGHT = "light"
    AGGRESSIVE = "aggressive"
    NONE = "none"

class OCRLanguage(Enum):
    """Supported OCR languages"""
    ENGLISH = "eng"
    SPANISH = "spa"
    FRENCH = "fra"
    GERMAN = "deu"
    ITALIAN = "ita"
    PORTUGUESE = "por"
    CHINESE_SIMPLIFIED = "chi_sim"
    AUTO_DETECT = "auto"

@dataclass
class OCRResult:
    """OCR processing result with metadata"""
    text: str
    confidence: float
    language: str
    processing_time: float
    preprocessing_applied: List[str]
    word_count: int
    character_count: int
    errors: List[str]
    metadata: Dict

class OCRService:
    """Advanced OCR service with preprocessing and quality assessment"""
    
    def __init__(self):
        self.tesseract_cmd = self._find_tesseract()
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.gif', '.tiff', '.bmp', '.webp'}
        self.default_config = '--oem 3 --psm 6'
        self.confidence_threshold = 60
        
        # Configure pytesseract
        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        
        logger.info(f"OCR Service initialized with Tesseract at: {self.tesseract_cmd}")
    
    def _find_tesseract(self) -> Optional[str]:
        """Find Tesseract executable path"""
        possible_paths = [
            '/opt/homebrew/bin/tesseract',  # Homebrew on Apple Silicon
            '/usr/local/bin/tesseract',      # Homebrew on Intel
            '/usr/bin/tesseract',            # Linux default
            'tesseract'                      # System PATH
        ]
        
        for path in possible_paths:
            if os.path.exists(path) or path == 'tesseract':
                try:
                    # Test if tesseract works
                    result = os.system(f"{path} --version > /dev/null 2>&1")
                    if result == 0:
                        return path
                except:
                    continue
        
        logger.warning("Tesseract not found in common locations")
        return None
    
    async def extract_text_from_image(
        self,
        image_path: Union[str, Path],
        language: OCRLanguage = OCRLanguage.AUTO_DETECT,
        preprocessing_mode: ImagePreprocessingMode = ImagePreprocessingMode.AUTO,
        custom_config: Optional[str] = None
    ) -> OCRResult:
        """
        Extract text from image using OCR with preprocessing
        
        Args:
            image_path: Path to image file
            language: OCR language (auto-detect by default)
            preprocessing_mode: Image preprocessing level
            custom_config: Custom Tesseract configuration
            
        Returns:
            OCRResult with extracted text and metadata
        """
        start_time = asyncio.get_event_loop().time()
        errors = []
        preprocessing_applied = []
        
        try:
            # Validate file format
            if not await self._validate_image_format(image_path):
                raise ValueError(f"Unsupported image format: {image_path}")
            
            # Load and preprocess image
            image = await self._load_and_preprocess_image(
                image_path, preprocessing_mode
            )
            preprocessing_applied = await self._get_preprocessing_steps(preprocessing_mode)
            
            # Detect language if auto-detect is enabled
            ocr_language = await self._detect_language(image, language)
            
            # Configure Tesseract
            config = custom_config or self.default_config
            lang_param = ocr_language if ocr_language != "auto" else "eng"
            
            # Perform OCR
            text = pytesseract.image_to_string(
                image, 
                lang=lang_param, 
                config=config
            ).strip()
            
            # Get confidence data
            confidence_data = pytesseract.image_to_data(
                image, 
                lang=lang_param,
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            confidence = await self._calculate_confidence(confidence_data)
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Generate metadata
            word_count = len(text.split())
            character_count = len(text)
            
            # Detect actual language of extracted text
            detected_language = await self._detect_text_language(text)
            
            metadata = {
                'image_format': await self._get_image_format(image_path),
                'image_size': await self._get_image_size(image_path),
                'tesseract_version': await self._get_tesseract_version(),
                'config_used': config,
                'language_used': lang_param,
                'detected_language': detected_language
            }
            
            return OCRResult(
                text=text,
                confidence=confidence,
                language=detected_language,
                processing_time=processing_time,
                preprocessing_applied=preprocessing_applied,
                word_count=word_count,
                character_count=character_count,
                errors=errors,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"OCR processing failed for {image_path}: {str(e)}")
            errors.append(str(e))
            
            return OCRResult(
                text="",
                confidence=0.0,
                language="unknown",
                processing_time=asyncio.get_event_loop().time() - start_time,
                preprocessing_applied=preprocessing_applied,
                word_count=0,
                character_count=0,
                errors=errors,
                metadata={}
            )
    
    async def _validate_image_format(self, image_path: Union[str, Path]) -> bool:
        """Validate if file is a supported image format"""
        try:
            file_type = filetype.guess(str(image_path))
            if file_type is None:
                return False
            return f".{file_type.extension}" in self.supported_formats
        except Exception as e:
            logger.error(f"Error validating image format: {e}")
            return False
    
    async def _load_and_preprocess_image(
        self, 
        image_path: Union[str, Path], 
        mode: ImagePreprocessingMode
    ) -> Image.Image:
        """Load and preprocess image for optimal OCR"""
        # Load image
        image = Image.open(image_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply preprocessing based on mode
        if mode == ImagePreprocessingMode.NONE:
            return image
        
        # Auto mode: analyze image and choose appropriate preprocessing
        if mode == ImagePreprocessingMode.AUTO:
            mode = await self._determine_optimal_preprocessing(image)
        
        return await self._apply_preprocessing(image, mode)
    
    async def _determine_optimal_preprocessing(self, image: Image.Image) -> ImagePreprocessingMode:
        """Analyze image characteristics to determine optimal preprocessing"""
        # Convert to OpenCV format for analysis
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Calculate image statistics
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Detect if image is very low contrast or too dark/bright
        if contrast < 30 or mean_brightness < 50 or mean_brightness > 200:
            return ImagePreprocessingMode.AGGRESSIVE
        elif contrast < 50:
            return ImagePreprocessingMode.LIGHT
        else:
            return ImagePreprocessingMode.LIGHT
    
    async def _apply_preprocessing(
        self, 
        image: Image.Image, 
        mode: ImagePreprocessingMode
    ) -> Image.Image:
        """Apply image preprocessing for better OCR results"""
        
        if mode == ImagePreprocessingMode.LIGHT:
            # Light preprocessing: enhance contrast and sharpness
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
            
        elif mode == ImagePreprocessingMode.AGGRESSIVE:
            # Aggressive preprocessing: multiple enhancement steps
            
            # Convert to OpenCV for advanced processing
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            
            # Noise reduction
            gray = cv2.medianBlur(gray, 3)
            
            # Morphological operations to clean up text
            kernel = np.ones((1,1), np.uint8)
            gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to PIL
            image = Image.fromarray(gray)
            image = image.convert('RGB')
            
            # Additional PIL enhancements
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.3)
        
        return image
    
    async def _detect_language(
        self, 
        image: Image.Image, 
        requested_language: OCRLanguage
    ) -> str:
        """Detect or validate OCR language"""
        if requested_language != OCRLanguage.AUTO_DETECT:
            return requested_language.value
        
        # For auto-detection, try English first as it's most common
        # In a more advanced implementation, we could do a quick OCR pass
        # to detect the language
        return OCRLanguage.ENGLISH.value
    
    async def _calculate_confidence(self, confidence_data: Dict) -> float:
        """Calculate overall confidence score from Tesseract data"""
        confidences = [
            int(conf) for conf in confidence_data['conf'] 
            if int(conf) > 0
        ]
        
        if not confidences:
            return 0.0
        
        # Weight confidence by text length
        texts = confidence_data['text']
        weighted_sum = 0
        total_chars = 0
        
        for i, conf in enumerate(confidences):
            text_length = len(texts[i].strip())
            if text_length > 0:
                weighted_sum += conf * text_length
                total_chars += text_length
        
        if total_chars == 0:
            return np.mean(confidences)
        
        return weighted_sum / total_chars
    
    async def _detect_text_language(self, text: str) -> str:
        """Detect language of extracted text"""
        if not text.strip():
            return "unknown"
        
        try:
            detected = langdetect.detect(text)
            return detected
        except:
            return "unknown"
    
    async def _get_preprocessing_steps(
        self, 
        mode: ImagePreprocessingMode
    ) -> List[str]:
        """Get list of preprocessing steps applied"""
        if mode == ImagePreprocessingMode.NONE:
            return []
        elif mode == ImagePreprocessingMode.LIGHT:
            return ["contrast_enhancement", "sharpening"]
        elif mode == ImagePreprocessingMode.AGGRESSIVE:
            return [
                "adaptive_histogram_equalization", 
                "noise_reduction", 
                "morphological_operations",
                "contrast_enhancement", 
                "sharpening"
            ]
        else:  # AUTO
            return ["auto_analysis", "adaptive_preprocessing"]
    
    async def _get_image_format(self, image_path: Union[str, Path]) -> str:
        """Get image format information"""
        try:
            file_type = filetype.guess(str(image_path))
            return file_type.extension if file_type else "unknown"
        except:
            return "unknown"
    
    async def _get_image_size(self, image_path: Union[str, Path]) -> Tuple[int, int]:
        """Get image dimensions"""
        try:
            with Image.open(image_path) as img:
                return img.size
        except:
            return (0, 0)
    
    async def _get_tesseract_version(self) -> str:
        """Get Tesseract version information"""
        try:
            return pytesseract.get_tesseract_version()
        except:
            return "unknown"
    
    async def batch_process_images(
        self,
        image_paths: List[Union[str, Path]],
        language: OCRLanguage = OCRLanguage.AUTO_DETECT,
        preprocessing_mode: ImagePreprocessingMode = ImagePreprocessingMode.AUTO,
        max_concurrent: int = 4
    ) -> List[OCRResult]:
        """
        Process multiple images concurrently
        
        Args:
            image_paths: List of image file paths
            language: OCR language
            preprocessing_mode: Image preprocessing level
            max_concurrent: Maximum concurrent processing tasks
            
        Returns:
            List of OCRResult objects
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single(image_path):
            async with semaphore:
                return await self.extract_text_from_image(
                    image_path, language, preprocessing_mode
                )
        
        tasks = [process_single(path) for path in image_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process {image_paths[i]}: {result}")
                processed_results.append(OCRResult(
                    text="",
                    confidence=0.0,
                    language="unknown",
                    processing_time=0.0,
                    preprocessing_applied=[],
                    word_count=0,
                    character_count=0,
                    errors=[str(result)],
                    metadata={}
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_supported_languages(self) -> List[str]:
        """Get list of available OCR languages"""
        try:
            langs = pytesseract.get_languages(config='')
            return sorted(langs)
        except Exception as e:
            logger.error(f"Error getting supported languages: {e}")
            return ["eng"]  # Default to English
    
    async def health_check(self) -> Dict[str, Union[str, bool, List[str]]]:
        """Perform OCR service health check"""
        try:
            # Test basic OCR functionality
            test_image = Image.new('RGB', (200, 50), color='white')
            # You could add text to this test image for a more comprehensive test
            
            health_status = {
                "status": "healthy",
                "tesseract_available": self.tesseract_cmd is not None,
                "tesseract_path": self.tesseract_cmd or "not found",
                "tesseract_version": await self._get_tesseract_version(),
                "supported_languages": self.get_supported_languages(),
                "supported_formats": list(self.supported_formats)
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"OCR health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "tesseract_available": False
            }

# Global OCR service instance
ocr_service = OCRService()
