"""
Process event analyzer for EventID 1 (Sysmon) and 4688 (Windows Security).

Analyzes process creation events for suspicious activity.
"""

from typing import Dict, Any, List, Tuple
from analyzers.base_analyzer import BaseAnalyzer
from models.analysis_result import EventAnalysis, SeverityLevel
from rules import suspicious_patterns, normal_patterns


class ProcessAnalyzer(BaseAnalyzer):
    """Analyzes process creation events."""
    
    # Event IDs this analyzer handles
    SUPPORTED_EVENT_IDS = [1, 4688]
    
    def can_analyze(self, event: Dict[str, Any]) -> bool:
        """Check if event is a process creation event."""
        event_id = self.get_field_value(event, 'event_id')
        if not event_id:
            event_id = self.get_field_value(event, 'EventID')
        
        try:
            return int(event_id) in self.SUPPORTED_EVENT_IDS
        except (ValueError, TypeError):
            return False
    
    def analyze(self, event: Dict[str, Any]) -> EventAnalysis:
        """Analyze process creation event."""
        # Extract event metadata
        event_id = self.get_field_value(event, 'event_id', 
                                       self.get_field_value(event, 'EventID', 'Unknown'))
        timestamp = self.extract_timestamp(event)
        
        # Extract process details - try both Sysmon and Security log formats
        image = self.get_field_value(event, 'Image', 
                                     self.get_field_value(event, 'NewProcessName', ''))
        command_line = self.get_field_value(event, 'CommandLine', '')
        parent_image = self.get_field_value(event, 'ParentImage',
                                           self.get_field_value(event, 'ParentProcessName', ''))
        user = self.get_field_value(event, 'User',
                                    self.get_field_value(event, 'SubjectUserName', ''))
        
        # Extract process name from path
        process_name = image.split('\\')[-1].lower() if image else ''
        parent_name = parent_image.split('\\')[-1].lower() if parent_image else ''
        
        # Analyze for suspicious patterns
        indicators = []
        field_references = []
        mitre_techniques = []
        severity = SeverityLevel.LOW
        analysis_text = ""
        
        # Check if normal process first
        is_normal, normal_reason = normal_patterns.is_legitimate_process(process_name, image)
        
        if not is_normal:
            # Check suspicious process
            if process_name in suspicious_patterns.SUSPICIOUS_PROCESSES:
                info = suspicious_patterns.SUSPICIOUS_PROCESSES[process_name]
                indicators.append(f"Suspicious process: {info['description']}")
                field_references.append(f"Image={image}")
                mitre_techniques.extend(info['techniques'])
                severity = max(severity, SeverityLevel.MEDIUM)
            
            # Check AppData executable
            if suspicious_patterns.is_appdata_executable(image):
                indicators.append("Executable in AppData directory (unusual for legitimate software)")
                field_references.append(f"Image={image}")
                mitre_techniques.append('T1036')  # Masquerading
                severity = max(severity, SeverityLevel.HIGH)
            
            # Check command line patterns
            if command_line:
                cmd_patterns = suspicious_patterns.get_command_pattern_info(command_line)
                if cmd_patterns:
                    for pattern, description, techniques in cmd_patterns:
                        indicators.append(f"Suspicious command: {description}")
                        mitre_techniques.extend(techniques)
                    field_references.append(f"CommandLine={command_line}")
                    severity = max(severity, SeverityLevel.HIGH)
            
            # Check parent-child relationships
            suspicious_spawn = self._check_suspicious_spawn(parent_name, process_name)
            if suspicious_spawn:
                indicators.append(suspicious_spawn)
                field_references.append(f"ParentImage={parent_image}")
                field_references.append(f"Image={image}")
                severity = max(severity, SeverityLevel.HIGH)
            
            # Build analysis text
            if indicators:
                analysis_text = f"Process {process_name} spawned by {parent_name}. "
                analysis_text += " | ".join(indicators)
            else:
                analysis_text = f"Process {process_name} executed normally by {user}."
        else:
            # Normal process
            analysis_text = f"Legitimate process {process_name}. {normal_reason}"
            field_references.append(f"Image={image}")
        
        return EventAnalysis(
            event_id=str(event_id),
            event_type='Process',
            timestamp=timestamp,
            analysis_text=analysis_text,
            indicators=indicators,
            severity=severity,
            field_references=field_references,
            mitre_techniques=list(set(mitre_techniques))  # Deduplicate
        )
    
    def _check_suspicious_spawn(self, parent: str, child: str) -> str:
        """
        Check for suspicious parent-child process relationships.
        
        Args:
            parent: Parent process name
            child: Child process name
            
        Returns:
            Suspicious relationship description or empty string
        """
        suspicious_pairs = [
            ('winword.exe', 'powershell.exe', 'Office spawning PowerShell (possible macro)'),
            ('excel.exe', 'powershell.exe', 'Office spawning PowerShell (possible macro)'),
            ('winword.exe', 'cmd.exe', 'Office spawning command shell (possible macro)'),
            ('excel.exe', 'cmd.exe', 'Office spawning command shell (possible macro)'),
            ('cmd.exe', 'powershell.exe', 'Command shell spawning PowerShell'),
            ('powershell.exe', 'net.exe', 'PowerShell spawning net commands'),
            ('powershell.exe', 'netsh.exe', 'PowerShell spawning netsh (firewall manipulation)'),
            ('rundll32.exe', 'powershell.exe', 'Rundll32 spawning PowerShell'),
            ('wscript.exe', 'powershell.exe', 'Script host spawning PowerShell'),
            ('cscript.exe', 'powershell.exe', 'Script host spawning PowerShell'),
        ]
        
        for parent_pattern, child_pattern, description in suspicious_pairs:
            if parent == parent_pattern and child == child_pattern:
                return description
        
        return ""
