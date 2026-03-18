"""
Formatter for suspicious/attack log analysis.

Generates detailed, field-specific explanations for malicious activity.
Emphasizes MITRE techniques, severity, and event correlations.
"""

from typing import List
from formatters.base_formatter import BaseFormatter
from models.analysis_result import AnalysisResult, SeverityLevel


class SuspiciousFormatter(BaseFormatter):
    """Formats suspicious activity analysis."""
    
    def format(self, analysis: AnalysisResult) -> str:
        """
        Format suspicious analysis with:
        1. Executive summary with severity
        2. Event-by-event breakdown
        3. MITRE ATT&CK techniques
        4. Attack chain correlation
        5. Specific field references
        
        Args:
            analysis: Analysis result
            
        Returns:
            Formatted output string
        """
        output_parts = []
        
        # 1. Executive summary
        total_events = len(analysis.event_analyses)
        suspicious_events = [e for e in analysis.event_analyses if e.indicators]
        suspicious_count = len(suspicious_events)
        
        # Determine overall severity
        max_severity = SeverityLevel.LOW
        for event in suspicious_events:
            if event.severity > max_severity:
                max_severity = event.severity
        
        summary = f"**SECURITY ALERT**: {suspicious_count} out of {total_events} events show malicious activity "
        summary += f"(Severity: {max_severity.name})"
        output_parts.append(summary)
        
        # 2. Event-by-event breakdown
        output_parts.append("\n**Suspicious Events Detected:**")
        
        for i, event in enumerate(suspicious_events, 1):
            event_desc = f"\n{i}. [{event.event_type}] EventID {event.event_id}"
            if event.timestamp:
                event_desc += f" at {event.timestamp}"
            event_desc += f" - {event.severity.name} SEVERITY"
            output_parts.append(event_desc)
            
            # Add analysis text
            output_parts.append(f"   Analysis: {event.analysis_text}")
            
            # Add indicators
            if event.indicators:
                output_parts.append("   Indicators:")
                for indicator in event.indicators:
                    output_parts.append(f"   - {indicator}")
            
            # Add field references
            if event.field_references:
                output_parts.append("   Referenced Fields:")
                for field_ref in event.field_references[:5]:  # Limit to 5 most important
                    output_parts.append(f"   - {field_ref}")
        
        # 3. MITRE ATT&CK techniques
        all_techniques = []
        for event in suspicious_events:
            all_techniques.extend(event.mitre_techniques)
        
        if all_techniques:
            unique_techniques = sorted(set(all_techniques))
            output_parts.append(f"\n**MITRE ATT&CK Techniques Observed:** {', '.join(unique_techniques)}")
        
        # 4. Attack chain correlation
        attack_chain = analysis.metadata.get('attack_chain', '')
        if attack_chain:
            output_parts.append(f"\n**Attack Chain Identified:** {attack_chain}")
        
        # 5. Recommendation
        if max_severity == SeverityLevel.CRITICAL:
            output_parts.append("\n**RECOMMENDATION**: Immediate investigation required. Potential active threat.")
        elif max_severity == SeverityLevel.HIGH:
            output_parts.append("\n**RECOMMENDATION**: High-priority investigation. Likely malicious activity.")
        elif max_severity == SeverityLevel.MEDIUM:
            output_parts.append("\n**RECOMMENDATION**: Further analysis needed. Suspicious patterns detected.")
        
        # Join and truncate if needed
        full_output = "\n".join(output_parts)
        return self.truncate_text(full_output, max_length=800)
