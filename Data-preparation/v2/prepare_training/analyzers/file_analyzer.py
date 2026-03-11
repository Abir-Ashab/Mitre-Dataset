"""
File event analyzer for EventID 11 (Sysmon File Create).

Analyzes file creation events for ransomware, malware staging, etc.
Based on real 7-Zip ransomware traces from user's documentation.
"""

from typing import Dict, Any, List
from analyzers.base_analyzer import BaseAnalyzer
from models.analysis_result import EventAnalysis, SeverityLevel
from rules import suspicious_patterns, normal_patterns


class FileAnalyzer(BaseAnalyzer):
    """Analyzes file creation/modification events."""
    
    # Event IDs this analyzer handles
    SUPPORTED_EVENT_IDS = [11, 23]  # 11=FileCreate, 23=FileDelete (Sysmon)
    
    def can_analyze(self, event: Dict[str, Any]) -> bool:
        """Check if event is a file operation event."""
        event_id = self.get_field_value(event, 'event_id')
        if not event_id:
            event_id = self.get_field_value(event, 'EventID')
        
        try:
            return int(event_id) in self.SUPPORTED_EVENT_IDS
        except (ValueError, TypeError):
            return False
    
    def analyze(self, event: Dict[str, Any]) -> EventAnalysis:
        """Analyze file operation event."""
        # Extract event metadata
        event_id = self.get_field_value(event, 'event_id',
                                       self.get_field_value(event, 'EventID', 'Unknown'))
        timestamp = self.extract_timestamp(event)
        
        # Extract file details
        target_filename = self.get_field_value(event, 'TargetFilename', '')
        image = self.get_field_value(event, 'Image', '')
        process_name = image.split('\\')[-1].lower() if image else 'unknown'
        
        # File extension
        file_ext = ''
        if target_filename and '.' in target_filename:
            file_ext = target_filename.split('.')[-1].lower()
        
        # Analyze for suspicious patterns
        indicators = []
        field_references = []
        mitre_techniques = []
        severity = SeverityLevel.LOW
        analysis_text = ""
        
        # Check for ransomware activity (from user's 7-Zip ransomware traces)
        ransomware_indicators = self._check_ransomware_patterns(
            process_name, target_filename, file_ext
        )
        if ransomware_indicators:
            indicators.extend(ransomware_indicators)
            field_references.append(f"TargetFilename={target_filename}")
            field_references.append(f"Image={image}")
            mitre_techniques.extend(['T1486', 'T1560.001'])  # Data Encrypted for Impact, Archive via Utility
            severity = max(severity, SeverityLevel.CRITICAL)
        
        # Check for executable in suspicious location
        if file_ext in ['exe', 'dll', 'sys', 'bat', 'ps1', 'vbs']:
            if 'AppData' in target_filename or 'Temp' in target_filename or 'Downloads' in target_filename:
                indicators.append(f"Executable file created in suspicious location: {target_filename}")
                field_references.append(f"TargetFilename={target_filename}")
                mitre_techniques.append('T1036')  # Masquerading
                severity = max(severity, SeverityLevel.HIGH)
        
        # Check for suspicious process creating files
        if process_name in suspicious_patterns.SUSPICIOUS_PROCESSES:
            info = suspicious_patterns.SUSPICIOUS_PROCESSES[process_name]
            indicators.append(f"File created by suspicious process: {info['description']}")
            field_references.append(f"Image={image}")
            mitre_techniques.extend(info['techniques'])
            severity = max(severity, SeverityLevel.MEDIUM)
        
        # Build analysis text
        if indicators:
            analysis_text = f"File {target_filename} created by {process_name}. "
            analysis_text += " | ".join(indicators)
        else:
            # Normal file operation
            if file_ext in normal_patterns.NORMAL_FILE_EXTENSIONS:
                analysis_text = f"Normal file creation: {target_filename} by {process_name}"
            else:
                analysis_text = f"File created: {target_filename} by {process_name}"
            field_references.append(f"TargetFilename={target_filename}")
        
        return EventAnalysis(
            event_id=str(event_id),
            event_type='File',
            timestamp=timestamp,
            analysis_text=analysis_text,
            indicators=indicators,
            severity=severity,
            field_references=field_references,
            mitre_techniques=list(set(mitre_techniques))
        )
    
    def _check_ransomware_patterns(self, process_name: str, filename: str, file_ext: str) -> List[str]:
        """
        Check for ransomware patterns based on user's 7-Zip ransomware traces.
        
        Patterns from ransom_trace.md:
        - 7z.exe creating many .7z files
        - High rate of file creates (>20 in 5 minutes threshold)
        - Mass file operations
        
        Args:
            process_name: Process creating file
            filename: Target filename
            file_ext: File extension
            
        Returns:
            List of ransomware indicators
        """
        indicators = []
        
        # Check 7-Zip archiving (from user's traces)
        if process_name == '7z.exe':
            if file_ext == '7z':
                indicators.append("7-Zip archiving activity - potential ransomware compression (T1560.001)")
            else:
                indicators.append("7z.exe file activity - monitor for mass operations")
        
        # Check archive extensions
        if file_ext in suspicious_patterns.RANSOMWARE_INDICATORS['archive_extensions']:
            indicators.append(f"Archive file creation (.{file_ext}) - verify legitimacy")
        
        # Check if file is in user directories (common ransomware target)
        if any(keyword in filename.lower() for keyword in ['documents', 'desktop', 'downloads', 'pictures']):
            if file_ext in ['7z', 'zip', 'rar']:
                indicators.append("Archive created in user directory - potential data staging for ransomware")
        
        return indicators
