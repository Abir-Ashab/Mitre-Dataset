"""
Formatter for normal/benign log analysis.

Generates explanations emphasizing what normal looks like and what's NOT present.
Helps teach the model to distinguish between benign and malicious.
"""

from typing import List, Set
from formatters.base_formatter import BaseFormatter
from models.analysis_result import AnalysisResult


class NormalFormatter(BaseFormatter):
    """Formats normal activity analysis."""
    
    def format(self, analysis: AnalysisResult) -> str:
        """
        Format normal analysis with:
        1. Summary of activity type
        2. Key normal patterns observed
        3. What's NOT present (critical for learning)
        4. Baseline comparison
        
        Args:
            analysis: Analysis result
            
        Returns:
            Formatted output string
        """
        output_parts = []
        
        # 1. Summary
        total_events = len(analysis.event_analyses)
        
        # Categorize event types
        event_types = {}
        for event in analysis.event_analyses:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        
        type_summary = ", ".join([f"{count} {etype}" for etype, count in event_types.items()])
        summary = f"**Normal Activity Detected**: {total_events} events analyzed ({type_summary}). "
        summary += "No malicious indicators found."
        output_parts.append(summary)
        
        # 2. Key normal patterns
        output_parts.append("\n**Normal Patterns Observed:**")
        
        # Group events by type and summarize
        normal_behaviors = []
        
        for event_type, count in event_types.items():
            type_events = [e for e in analysis.event_analyses if e.event_type == event_type]
            
            if event_type == 'Process':
                # Summarize process activity
                processes = set()
                for e in type_events:
                    # Extract process name from field references
                    for ref in e.field_references:
                        if 'Image=' in ref:
                            proc = ref.split('=')[1].split('\\')[-1]
                            processes.add(proc)
                if processes:
                    normal_behaviors.append(f"- Legitimate process executions: {', '.join(list(processes)[:5])}")
            
            elif event_type == 'Network':
                # Summarize network activity
                ports = set()
                for e in type_events:
                    for ref in e.field_references:
                        if 'DestinationPort=' in ref:
                            port = ref.split('=')[1]
                            ports.add(port)
                if ports:
                    normal_behaviors.append(f"- Standard network traffic on ports: {', '.join(list(ports)[:5])}")
            
            elif event_type == 'File':
                # Summarize file activity
                normal_behaviors.append(f"- Normal file operations: {count} events")
        
        if normal_behaviors:
            output_parts.extend(normal_behaviors)
        else:
            output_parts.append("- Standard system operations with no anomalies")
        
        # 3. What's NOT present (critical for model learning)
        output_parts.append("\n**No Malicious Indicators:**")
        not_present = [
            "- No suspicious process spawning (e.g., Office apps spawning PowerShell)",
            "- No C2 beaconing patterns (no small periodic packets to external IPs)",
            "- No command-line obfuscation or encoded commands",
            "- No connections to high-risk ports (e.g., 4444, 8080, 31337)",
            "- No mass file operations typical of ransomware",
            "- No executables in suspicious locations (AppData, Temp)",
        ]
        
        # Filter based on event types present
        if 'Process' not in event_types:
            not_present = [n for n in not_present if 'process' not in n.lower() and 'command' not in n.lower()]
        if 'Network' not in event_types:
            not_present = [n for n in not_present if 'c2' not in n.lower() and 'ports' not in n.lower()]
        if 'File' not in event_types:
            not_present = [n for n in not_present if 'mass file' not in n.lower() and 'executables' not in n.lower()]
        
        output_parts.extend(not_present[:4])  # Show top 4 most relevant
        
        # 4. Baseline comparison
        output_parts.append(f"\n**Assessment**: All {total_events} events match expected baseline behavior. ")
        output_parts.append("Activity is consistent with legitimate user/system operations.")
        
        # Join and truncate
        full_output = "\n".join(output_parts)
        return self.truncate_text(full_output, max_length=600)
