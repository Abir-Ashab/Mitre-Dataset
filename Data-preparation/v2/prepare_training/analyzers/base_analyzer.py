"""
Base analyzer interface following Interface Segregation Principle.

All analyzers should implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from models.analysis_result import EventAnalysis


class BaseAnalyzer(ABC):
    """Abstract base class for event analyzers."""
    
    @abstractmethod
    def analyze(self, event: Dict[str, Any]) -> EventAnalysis:
        """
        Analyze a single event and return analysis result.
        
        Args:
            event: Log event dictionary
            
        Returns:
            EventAnalysis object with analysis details
        """
        pass
    
    @abstractmethod
    def can_analyze(self, event: Dict[str, Any]) -> bool:
        """
        Check if this analyzer can handle the given event.
        
        Args:
            event: Log event dictionary
            
        Returns:
            True if analyzer can process this event type
        """
        pass
    
    def get_field_value(self, event: Dict[str, Any], field: str, default: Any = "") -> Any:
        """
        Safely extract field value from event.
        
        Args:
            event: Event dictionary
            field: Field name (supports nested keys with dots)
            default: Default value if field not found
            
        Returns:
            Field value or default
        """
        keys = field.split('.')
        value = event
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value if value != "" else default
    
    def extract_timestamp(self, event: Dict[str, Any]) -> str:
        """
        Extract timestamp from event, trying common field names.
        
        Args:
            event: Event dictionary
            
        Returns:
            Timestamp string or empty string
        """
        for field in ['timestamp', 'Timestamp', '@timestamp', 'time', 'TimeCreated']:
            ts = self.get_field_value(event, field)
            if ts:
                return str(ts)
        return ""
