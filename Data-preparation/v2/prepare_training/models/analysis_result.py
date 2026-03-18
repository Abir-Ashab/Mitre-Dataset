"""
Data models for log analysis results.

Provides structured types for passing analysis data between components.
Follows the Single Responsibility Principle - each class has one clear purpose.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class IndicatorType(Enum):
    """Types of security indicators."""
    PROCESS_EXECUTION = "process_execution"
    NETWORK_CONNECTION = "network_connection"
    REGISTRY_MODIFICATION = "registry_modification"
    FILE_OPERATION = "file_operation"
    CREDENTIAL_ACCESS = "credential_access"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class SeverityLevel(Enum):
    """Severity levels for threat assessment."""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1
    
    def __lt__(self, other):
        if not isinstance(other, SeverityLevel):
            return NotImplemented
        return self.value < other.value
    
    def __le__(self, other):
        if not isinstance(other, SeverityLevel):
            return NotImplemented
        return self.value <= other.value
    
    def __gt__(self, other):
        if not isinstance(other, SeverityLevel):
            return NotImplemented
        return self.value > other.value
    
    def __ge__(self, other):
        if not isinstance(other, SeverityLevel):
            return NotImplemented
        return self.value >= other.value


@dataclass
class EventAnalysis:
    """
    Analysis result for a single log event.
    
    Attributes:
        event_id: Windows Event ID (e.g., 4688, 3, 13)
        event_type: Human-readable event type
        timestamp: Event timestamp
        analysis_text: Detailed analysis explanation
        indicators: List of threat indicators found
        severity: Severity assessment
        field_references: Specific log fields referenced in analysis
        mitre_techniques: MITRE ATT&CK techniques identified
    """
    event_id: str
    event_type: str
    timestamp: str
    analysis_text: str
    indicators: List[str] = field(default_factory=list)
    severity: SeverityLevel = SeverityLevel.INFO
    field_references: Dict[str, str] = field(default_factory=dict)
    mitre_techniques: List[str] = field(default_factory=list)
    
    def to_formatted_string(self, index: int) -> str:
        """
        Format event analysis as human-readable string.
        
        Args:
            index: Event number in sequence
            
        Returns:
            Formatted analysis string
        """
        parts = [
            f"{index}. {self.event_type} [{self.event_id}] at {self.timestamp} (Severity: {self.severity.name}):",
            f"   {self.analysis_text}"
        ]
        
        if self.indicators:
            parts.append(f"   Threat Indicators: {' | '.join(self.indicators)}")
        
        return "\n".join(parts)


@dataclass
class AnalysisResult:
    """
    Complete analysis result for a log chunk.
    
    Attributes:
        is_suspicious: Whether chunk contains suspicious activity
        event_analyses: List of individual event analyses
        correlations: Cross-event correlations detected
        mitre_techniques: All MITRE techniques identified
        max_severity: Highest severity level found
        confidence: Analysis confidence level
        metadata: Additional analysis metadata
    """
    is_suspicious: bool
    event_analyses: List[EventAnalysis] = field(default_factory=list)
    correlations: List[str] = field(default_factory=list)
    mitre_techniques: List[str] = field(default_factory=list)
    max_severity: SeverityLevel = SeverityLevel.INFO
    confidence: str = "medium"
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def add_event_analysis(self, analysis: EventAnalysis) -> None:
        """Add an event analysis and update aggregate fields."""
        self.event_analyses.append(analysis)
        
        # Update max severity using comparison operators
        if analysis.severity > self.max_severity:
            self.max_severity = analysis.severity
        
        # Collect MITRE techniques
        for technique in analysis.mitre_techniques:
            if technique not in self.mitre_techniques:
                self.mitre_techniques.append(technique)
    
    def get_indicator_count(self) -> int:
        """Get total number of unique indicators."""
        all_indicators = set()
        for analysis in self.event_analyses:
            all_indicators.update(analysis.indicators)
        return len(all_indicators)
    
    def get_suspicious_event_count(self) -> int:
        """Get count of events with indicators."""
        return sum(1 for analysis in self.event_analyses if analysis.indicators)
