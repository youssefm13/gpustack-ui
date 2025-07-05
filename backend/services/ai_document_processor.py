"""
AI-Powered Document Processor for GPUStack UI
Enhances file processing with LLM-based intelligence, summarization, and semantic analysis.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import re
from pathlib import Path

from .inference_client import send_to_gpustack
from .file_processor import file_processor

logger = logging.getLogger(__name__)

class DocumentAnalysisMode(Enum):
    """Different modes for document analysis"""
    QUICK = "quick"           # Fast analysis for real-time use
    DETAILED = "detailed"      # Comprehensive analysis
    SEMANTIC = "semantic"      # Deep semantic understanding
    STRUCTURED = "structured"  # Focus on document structure

@dataclass
class DocumentInsight:
    """AI-generated insights about a document"""
    summary: str
    key_points: List[str]
    topics: List[str]
    sentiment: str
    complexity_score: float
    reading_time_minutes: int
    target_audience: str
    document_type: str
    confidence_score: float

@dataclass
class SemanticChunk:
    """Semantically meaningful chunk of content"""
    content: str
    topic: str
    importance_score: float
    context: Dict[str, Any]
    start_position: int
    end_position: int

class AIDocumentProcessor:
    """
    AI-powered document processor that enhances file processing with LLM intelligence.
    Provides intelligent summarization, key point extraction, and semantic analysis.
    """
    
    def __init__(self):
        self.max_chunk_size = 4000  # Optimal for LLM processing
        self.summary_max_length = 500
        self.key_points_max_count = 10
        self.complexity_thresholds = {
            "simple": 0.3,
            "moderate": 0.6,
            "complex": 1.0
        }
        # Higher max_tokens defaults for more comprehensive responses
        self.max_tokens_quick = 4000      # Increased from 800
        self.max_tokens_detailed = 8000   # Increased from 1200
        self.max_tokens_semantic = 4000   # Increased from 1000
        self.max_tokens_structured = 4000 # Increased from 1000
    
    async def enhance_document_processing(
        self, 
        file_result: Dict[str, Any],
        mode: DocumentAnalysisMode = DocumentAnalysisMode.QUICK
    ) -> Dict[str, Any]:
        """
        Enhance document processing with AI-powered analysis.
        
        Args:
            file_result: Result from file_processor.process_file()
            mode: Analysis mode for different use cases
            
        Returns:
            Enhanced result with AI insights
        """
        try:
            content = file_result.get("content", "")
            if not content or len(content.strip()) < 50:
                return file_result  # Skip AI processing for very short content
            
            # Perform AI analysis based on mode
            if mode == DocumentAnalysisMode.QUICK:
                insights = await self._quick_analysis(content)
            elif mode == DocumentAnalysisMode.DETAILED:
                insights = await self._detailed_analysis(content)
            elif mode == DocumentAnalysisMode.SEMANTIC:
                insights = await self._semantic_analysis(content)
            elif mode == DocumentAnalysisMode.STRUCTURED:
                insights = await self._structured_analysis(content, file_result)
            else:
                insights = await self._quick_analysis(content)
            
            # Create semantic chunks for better context management
            semantic_chunks = await self._create_semantic_chunks(content, insights)
            
            # Enhance the original result
            enhanced_result = {
                **file_result,
                "ai_insights": insights,
                "semantic_chunks": semantic_chunks,
                "enhanced_content": await self._create_enhanced_content(content, insights),
                "processing_notes": file_result.get("processing_notes", []) + [
                    "AI-powered analysis applied",
                    f"Analysis mode: {mode.value}",
                    f"Generated {len(insights.key_points)} key points",
                    f"Complexity: {insights.complexity_score:.2f}"
                ]
            }
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"AI document processing failed: {str(e)}")
            # Return original result if AI processing fails
            return file_result
    
    async def _quick_analysis(self, content: str) -> DocumentInsight:
        """Fast analysis for real-time use cases."""
        
        prompt = f"""
        Analyze this document and provide a quick assessment:

        {content[:3000]}

        Provide a JSON response with:
        - summary: Brief 2-3 sentence summary
        - key_points: 3-5 main points (array of strings)
        - topics: 3-5 topics covered (array of strings)
        - sentiment: positive/neutral/negative
        - complexity_score: 0.0-1.0 (simple to complex)
        - reading_time_minutes: estimated reading time
        - target_audience: who this is written for
        - document_type: type of document
        - confidence_score: 0.0-1.0 (how confident in analysis)
        """
        
        try:
            response = await send_to_gpustack({
                "model": "qwen3",  # Use available model
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": self.max_tokens_quick
            })
            
            # Parse JSON response
            analysis_text = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            analysis_data = json.loads(analysis_text)
            
            return DocumentInsight(
                summary=analysis_data.get("summary", ""),
                key_points=analysis_data.get("key_points", []),
                topics=analysis_data.get("topics", []),
                sentiment=analysis_data.get("sentiment", "neutral"),
                complexity_score=float(analysis_data.get("complexity_score", 0.5)),
                reading_time_minutes=int(analysis_data.get("reading_time_minutes", 5)),
                target_audience=analysis_data.get("target_audience", "general"),
                document_type=analysis_data.get("document_type", "document"),
                confidence_score=float(analysis_data.get("confidence_score", 0.8))
            )
            
        except Exception as e:
            logger.error(f"Quick analysis failed: {str(e)}")
            return self._create_fallback_insight(content)
    
    async def _detailed_analysis(self, content: str) -> DocumentInsight:
        """Comprehensive analysis with detailed insights."""
        
        # Split content into chunks for detailed analysis
        chunks = self._split_content_into_chunks(content, self.max_chunk_size)
        
        detailed_prompt = f"""
        Perform a detailed analysis of this document:

        {content[:6000]}

        Provide a comprehensive JSON response with:
        - summary: Detailed 4-6 sentence summary
        - key_points: 5-10 main points with explanations
        - topics: Detailed topic breakdown
        - sentiment: Detailed sentiment analysis
        - complexity_score: Detailed complexity assessment
        - reading_time_minutes: Accurate reading time estimate
        - target_audience: Detailed audience analysis
        - document_type: Specific document classification
        - confidence_score: Confidence in analysis
        """
        
        try:
            response = await send_to_gpustack({
                "model": "qwen3-32b-bf16",  # Use available large model for detailed analysis
                "messages": [{"role": "user", "content": detailed_prompt}],
                "temperature": 0.2,
                "max_tokens": self.max_tokens_detailed
            })
            
            analysis_text = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            analysis_data = json.loads(analysis_text)
            
            return DocumentInsight(
                summary=analysis_data.get("summary", ""),
                key_points=analysis_data.get("key_points", []),
                topics=analysis_data.get("topics", []),
                sentiment=analysis_data.get("sentiment", "neutral"),
                complexity_score=float(analysis_data.get("complexity_score", 0.5)),
                reading_time_minutes=int(analysis_data.get("reading_time_minutes", 5)),
                target_audience=analysis_data.get("target_audience", "general"),
                document_type=analysis_data.get("document_type", "document"),
                confidence_score=float(analysis_data.get("confidence_score", 0.8))
            )
            
        except Exception as e:
            logger.error(f"Detailed analysis failed: {str(e)}")
            return await self._quick_analysis(content)
    
    async def _semantic_analysis(self, content: str) -> DocumentInsight:
        """Deep semantic understanding of document content."""
        
        semantic_prompt = f"""
        Perform semantic analysis of this document:

        {content[:4000]}

        Focus on:
        - Semantic meaning and implications
        - Context and relationships between concepts
        - Underlying themes and patterns
        - Semantic complexity and depth

        Provide JSON response with semantic insights.
        """
        
        try:
            response = await send_to_gpustack({
                "model": "qwen3",  # Use available model
                "messages": [{"role": "user", "content": semantic_prompt}],
                "temperature": 0.1,
                "max_tokens": self.max_tokens_semantic
            })
            
            analysis_text = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            analysis_data = json.loads(analysis_text)
            
            return DocumentInsight(
                summary=analysis_data.get("summary", ""),
                key_points=analysis_data.get("key_points", []),
                topics=analysis_data.get("topics", []),
                sentiment=analysis_data.get("sentiment", "neutral"),
                complexity_score=float(analysis_data.get("complexity_score", 0.5)),
                reading_time_minutes=int(analysis_data.get("reading_time_minutes", 5)),
                target_audience=analysis_data.get("target_audience", "general"),
                document_type=analysis_data.get("document_type", "document"),
                confidence_score=float(analysis_data.get("confidence_score", 0.8))
            )
            
        except Exception as e:
            logger.error(f"Semantic analysis failed: {str(e)}")
            return await self._quick_analysis(content)
    
    async def _structured_analysis(self, content: str, file_result: Dict[str, Any]) -> DocumentInsight:
        """Analysis that leverages document structure information."""
        
        structure_info = file_result.get("structure", {})
        headers = structure_info.get("headers", [])
        tables = structure_info.get("tables", [])
        
        structured_prompt = f"""
        Analyze this document considering its structure:

        Content: {content[:3000]}
        
        Document Structure:
        - Headers: {headers}
        - Tables: {tables}
        - Metadata: {file_result.get("metadata", {})}

        Provide structured analysis in JSON format.
        """
        
        try:
            response = await send_to_gpustack({
                "model": "qwen3",  # Use available model
                "messages": [{"role": "user", "content": structured_prompt}],
                "temperature": 0.3,
                "max_tokens": self.max_tokens_structured
            })
            
            analysis_text = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            analysis_data = json.loads(analysis_text)
            
            return DocumentInsight(
                summary=analysis_data.get("summary", ""),
                key_points=analysis_data.get("key_points", []),
                topics=analysis_data.get("topics", []),
                sentiment=analysis_data.get("sentiment", "neutral"),
                complexity_score=float(analysis_data.get("complexity_score", 0.5)),
                reading_time_minutes=int(analysis_data.get("reading_time_minutes", 5)),
                target_audience=analysis_data.get("target_audience", "general"),
                document_type=analysis_data.get("document_type", "document"),
                confidence_score=float(analysis_data.get("confidence_score", 0.8))
            )
            
        except Exception as e:
            logger.error(f"Structured analysis failed: {str(e)}")
            return await self._quick_analysis(content)
    
    async def _create_semantic_chunks(
        self, 
        content: str, 
        insights: DocumentInsight
    ) -> List[SemanticChunk]:
        """Create semantically meaningful chunks of content."""
        
        chunks = []
        words = content.split()
        chunk_size = 200  # words per chunk
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_content = " ".join(chunk_words)
            
            # Determine topic for this chunk
            topic = await self._determine_chunk_topic(chunk_content, insights.topics)
            
            # Calculate importance score
            importance_score = await self._calculate_chunk_importance(chunk_content, insights)
            
            chunks.append(SemanticChunk(
                content=chunk_content,
                topic=topic,
                importance_score=importance_score,
                context={
                    "position": i // chunk_size,
                    "total_chunks": len(words) // chunk_size + 1,
                    "word_count": len(chunk_words)
                },
                start_position=i,
                end_position=min(i + chunk_size, len(words))
            ))
        
        return chunks
    
    async def _determine_chunk_topic(self, chunk_content: str, available_topics: List[str]) -> str:
        """Determine the main topic of a content chunk."""
        if not available_topics:
            return "general"
        
        # Simple keyword matching for now
        chunk_lower = chunk_content.lower()
        for topic in available_topics:
            if topic.lower() in chunk_lower:
                return topic
        
        return available_topics[0] if available_topics else "general"
    
    async def _calculate_chunk_importance(self, chunk_content: str, insights: DocumentInsight) -> float:
        """Calculate importance score for a content chunk."""
        # Simple heuristics for importance scoring
        importance_score = 0.5  # Base score
        
        # Boost for key points
        chunk_lower = chunk_content.lower()
        for key_point in insights.key_points:
            if any(word in chunk_lower for word in key_point.lower().split()):
                importance_score += 0.2
        
        # Boost for headers/titles
        if any(word.isupper() for word in chunk_content.split()[:3]):
            importance_score += 0.1
        
        # Boost for numbers (might indicate important data)
        if re.search(r'\d+', chunk_content):
            importance_score += 0.05
        
        return min(importance_score, 1.0)
    
    async def _create_enhanced_content(self, content: str, insights: DocumentInsight) -> str:
        """Create enhanced content with AI insights integrated."""
        
        enhanced_content = f"""
=== AI-ENHANCED DOCUMENT ANALYSIS ===

 SUMMARY
{insights.summary}

🎯 KEY POINTS
{chr(10).join(f"• {point}" for point in insights.key_points)}

📚 TOPICS COVERED
{chr(10).join(f"• {topic}" for topic in insights.topics)}

📊 DOCUMENT METRICS
• Complexity: {insights.complexity_score:.2f}/1.0
• Reading Time: ~{insights.reading_time_minutes} minutes
• Target Audience: {insights.target_audience}
• Document Type: {insights.document_type}
• Sentiment: {insights.sentiment}
• Confidence: {insights.confidence_score:.2f}/1.0

=== ORIGINAL CONTENT ===
{content}
"""
        
        return enhanced_content
    
    def _split_content_into_chunks(self, content: str, max_chunk_size: int) -> List[str]:
        """Split content into manageable chunks."""
        words = content.split()
        chunks = []
        
        for i in range(0, len(words), max_chunk_size):
            chunk_words = words[i:i + max_chunk_size]
            chunks.append(" ".join(chunk_words))
        
        return chunks
    
    def _create_fallback_insight(self, content: str) -> DocumentInsight:
        """Create a fallback insight when AI analysis fails."""
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)  # 200 words per minute
        
        return DocumentInsight(
            summary="Document processed successfully. AI analysis unavailable.",
            key_points=["Content extracted and processed"],
            topics=["general"],
            sentiment="neutral",
            complexity_score=0.5,
            reading_time_minutes=reading_time,
            target_audience="general",
            document_type="document",
            confidence_score=0.5
        )

# Global instance
ai_document_processor = AIDocumentProcessor() 