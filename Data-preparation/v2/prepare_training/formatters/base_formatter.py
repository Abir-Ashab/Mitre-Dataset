"""
Base formatter interface for generating training outputs.

Formatters transform analysis results into training data format.
"""

from abc import ABC, abstractmethod
from typing import List
from models.analysis_result import AnalysisResult


class BaseFormatter(ABC):
    """Abstract base class for output formatters."""
    
    @abstractmethod
    def format(self, analysis: AnalysisResult) -> str:
        """
        Format analysis result into training output string.
        
        Args:
            analysis: Complete analysis result for log chunk
            
        Returns:
            Formatted string for training data output
        """
        pass
    
    def truncate_text(self, text: str, max_length: int = 500) -> str:
        """
        Truncate text to max length while preserving sentence boundaries.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        # Try to cut at sentence boundary
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        if last_period > max_length * 0.7:  # If sentence end is reasonable
            return truncated[:last_period + 1]
        
        return truncated[:max_length] + "..."
