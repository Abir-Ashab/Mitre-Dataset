"""
Suspicious patterns and indicators derived from real attack traces.

Based on actual attack scenarios documented in:
- E:\Hacking\Mitre-Dataset\docs\trace in logs\
- E:\Hacking\Mitre-Dataset\Annotate-attack-logs\helpers\

These patterns represent real-world attack behaviors observed during penetration testing.
Follows Open/Closed Principle - easy to extend with new patterns without modification.
"""

from typing import Dict, List, Set, Tuple

# ============================================================================
# PROCESS-BASED INDICATORS
# ============================================================================

# Suspicious executables commonly used in attacks
SUSPICIOUS_PROCESSES: Dict[str, Dict[str, any]] = {
    'powershell.exe': {
        'description': 'PowerShell - often used for remote execution',
        'techniques': ['T1059.001', 'T1105']
    },
    'cmd.exe': {
        'description': 'Command prompt - common for execution',
        'techniques': ['T1059.003']
    },
    'wscript.exe': {
        'description': 'Windows Script Host',
        'techniques': ['T1059.005']
    },
    'cscript.exe': {
        'description': 'Console Script Host', 
        'techniques': ['T1059.005']
    },
    'mshta.exe': {
        'description': 'Microsoft HTML Application Host',
        'techniques': ['T1218.005']
    },
    'rundll32.exe': {
        'description': 'DLL execution utility',
        'techniques': ['T1218.011']
    },
    'regsvr32.exe': {
        'description': 'DLL registration utility',
        'techniques': ['T1218.010']
    },
    'certutil.exe': {
        'description': 'Certificate utility (often used for downloads)',
        'techniques': ['T1105', 'T1027']
    },
    'bitsadmin.exe': {
        'description': 'BITS admin (used for file downloads)',
        'techniques': ['T1105', 'T1197']
    },
    'msiexec.exe': {
        'description': 'Windows Installer execution',
        'techniques': ['T1218.007']
    },
    '7z.exe': {
        'description': '7-Zip archiver (used in ransomware)',
        'techniques': ['T1560.001', 'T1486']
    },
    'winrar.exe': {
        'description': 'WinRAR archiver (compression/exfiltration)',
        'techniques': ['T1560.001']
    }
}

# Command-line patterns indicating malicious activity
SUSPICIOUS_COMMAND_PATTERNS: List[Tuple[str, str, List[str]]] = [
    # (pattern, description, mitre_techniques)
    ('Invoke-WebRequest', 'Remote file download via PowerShell', ['T1105', 'T1059.001']),
    ('Invoke-Expression', 'Dynamic code execution', ['T1059.001']),
    ('IEX', 'PowerShell Invoke-Expression alias', ['T1059.001']),
    ('DownloadString', 'Web-based code download', ['T1105', 'T1071.001']),
    ('DownloadFile', 'File download from remote', ['T1105']),
    ('Start-Process', 'Process spawning', ['T1106']),
    ('-EncodedCommand', 'Base64 encoded PowerShell command', ['T1027', 'T1059.001']),
    ('-ExecutionPolicy Bypass', 'Bypassing script execution controls', ['T1562.001', 'T1059.001']),
    ('-ep bypass', 'Execution policy bypass (short form)', ['T1562.001', 'T1059.001']),
    ('mimikatz', 'Credential dumping tool', ['T1003.001', 'T1003.002']),
    ('sekurlsa', 'Mimikatz credential extraction module', ['T1003.001']),
    ('lsadump', 'SAM/LSA dump for credential theft', ['T1003.002', 'T1003.004']),
    ('comsvcs.dll', 'LSASS memory dump via DLL', ['T1003.001']),
    ('MiniDump', 'Process memory dump function', ['T1003.001']),
    ('procdump', 'Sysinternals memory dump tool', ['T1003.001']),
    ('/compress', '7-Zip compression (ransomware)', ['T1560.001']),
    ('/encrypt', 'Encryption command', ['T1486']),
]

# AppData executables (often malware staging area)
APPDATA_SUSPICIOUS_PATTERNS: List[str] = [
    r'\\AppData\\Local\\Temp\\',
    r'\\AppData\\Roaming\\',
    r'\\AppData\\LocalLow\\',
]


# ============================================================================
# NETWORK-BASED INDICATORS  
# ============================================================================

# High-risk ports based on actual attack scenarios
HIGH_RISK_PORTS: Dict[int, Tuple[str, List[str]]] = {
    # (service_name, mitre_techniques)
    22: ('SSH', ['T1021.004', 'T1219']),
    23: ('Telnet', ['T1021', 'T1219']),
    445: ('SMB', ['T1021.002', 'T1570']),  # Lateral movement
    3389: ('RDP', ['T1021.001', 'T1219']),
    4444: ('Metasploit', ['T1071.001', 'T1571']),  # Classic C2 port
    5985: ('WinRM', ['T1021.006']),
    5986: ('WinRM HTTPS', ['T1021.006']),
    8080: ('HTTP Proxy/C2', ['T1071.001', 'T1090']),
    443: ('HTTPS C2', ['T1071.001', 'T1573.002']),  # When to non-standard domains
}

# C2 server indicators (from actual attack logs)
C2_INDICATORS: Dict[str, Dict[str, any]] = {
    'small_periodic_packets': {
        'min_size': 50,
        'max_size': 100,
        'techniques': ['T1071', 'T1571', 'T1090', 'T1572']
    },
    'external_ip_beaconing': {
        'techniques': ['T1071.001', 'T1090']
    },
    'non_standard_port_https': {
        'techniques': ['T1071.001', 'T1573.002']
    },
    'ack_only_keepalive': {
        'techniques': ['T1571']
    },
    'malware_download': {
        'min_packet_size': 500,
        'techniques': ['T1105']
    }
}

# Suspicious IP ranges (from actual attacks)
SUSPICIOUS_IP_PATTERNS: List[Tuple[str, str]] = [
    ('185.', 'Commonly associated with malicious infrastructure'),
    ('194.', 'Known hosting malicious services'),
    ('147.185.221.22', 'Documented C2 server from attack traces'),
    ('150.171.27.10', 'RevengeRAT C2 server from traces'),
]

# Download indicators (from download_trace.md)
DOWNLOAD_INDICATORS: Dict[str, Dict[str, any]] = {
    'large_inbound_tcp': {
        'min_size': 500,
        'techniques': ['T1105']
    },
    'raw_payload_series': {
        'techniques': ['T1105']
    },
    'file_transfer_volume': {
        'min_bytes': 1048576,  # 1MB
        'techniques': ['T1105', 'T1048']
    }
}


# ============================================================================
# FILE OPERATION INDICATORS (Ransomware traces)
# ============================================================================

# Ransomware file operations (from ransom_trace.md)
RANSOMWARE_INDICATORS: Dict[str, any] = {
    # Thresholds for mass operations
    'mass_file_creation': {
        'threshold': 20,
        'techniques': ['T1486', 'T1560.001']
    },
    'mass_file_deletion': {
        'threshold': 15,
        'techniques': ['T1485', 'T1486']
    },
    'high_io_burst': {
        'threshold': 50,
        'techniques': ['T1083', 'T1486']
    },
    '7z_spawn_frequency': {
        'threshold': 1,
        'techniques': ['T1560.001']
    },
    # Archive extensions to watch
    'archive_extensions': {'.7z', '.zip', '.rar'},
    # Encryption extensions
    'encryption_extensions': {'.encrypted', '.locked', '.crypto'}
}

# Suspicious file extensions for archival/encryption (for backward compatibility)
RANSOMWARE_EXTENSIONS: Set[str] = {
    '.7z', '.zip', '.rar',
    '.encrypted', '.locked', '.crypto',
}


# ============================================================================
# REGISTRY-BASED INDICATORS
# ============================================================================

SUSPICIOUS_REGISTRY_PATHS: List[Tuple[str, str, List[str]]] = [
    # (path_pattern, description, mitre_techniques)
    ('CurrentVersion\\Run', 'Persistence via Run key', ['T1547.001']),
    ('CurrentVersion\\RunOnce', 'Persistence via RunOnce key', ['T1547.001']),
    ('Winlogon', 'Logon script persistence', ['T1547.001']),
    ('UserInitMprLogonScript', 'User init persistence', ['T1547.001']),
    ('Image File Execution Options', 'Debugger persistence', ['T1546.012']),
]


# ============================================================================
# ATTACK CHAIN PATTERNS (Cross-event correlations)
# ============================================================================

ATTACK_CHAIN_PATTERNS: List[Dict[str, any]] = [
    {
        'name': 'malware_download_execute',
        'description': 'Download followed by execution',
        'sequence': ['network_download', 'process_execution'],
        'time_window_sec': 120,
        'mitre_techniques': ['T1105', 'T1204.002']
    },
    {
        'name': 'credential_dump_exfil',
        'description': 'Credential dumping followed by network exfiltration',
        'sequence': ['credential_access', 'network_upload'],
        'time_window_sec': 300,
        'mitre_techniques': ['T1003.001', 'T1041', 'T1071.001']
    },
    {
        'name': 'ransomware_chain',
        'description': '7-Zip compression, mass deletion, then potential exfil',
        'sequence': ['7z_spawn', 'mass_file_ops', 'network_activity'],
        'time_window_sec': 600,
        'mitre_techniques': ['T1560.001', 'T1486', 'T1041']
    },
    {
        'name': 'c2_beacon_with_execution',
        'description': 'Process execution followed by periodic C2 beaconing',
        'sequence': ['process_execution', 'periodic_network'],
        'time_window_sec': 300,
        'mitre_techniques': ['T1059', 'T1071.001', 'T1573']
    }
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_command_pattern_info(command_line: str) -> List[Tuple[str, str, List[str]]]:
    """
    Check command line against known suspicious patterns.
    
    Args:
        command_line: Command line string to analyze
        
    Returns:
        List of (pattern, description, techniques) tuples that matched
    """
    matches = []
    command_lower = command_line.lower()
    
    for pattern, description, techniques in SUSPICIOUS_COMMAND_PATTERNS:
        if pattern.lower() in command_lower:
            matches.append((pattern, description, techniques))
    
    return matches


def is_appdata_executable(path: str) -> bool:
    """
    Check if executable is in suspicious AppData location.
    
    Args:
        path: File path to check
        
    Returns:
        True if in suspicious AppData location
    """
    if not path:
        return False
    
    path_lower = path.lower()
    return any(pattern.lower() in path_lower for pattern in APPDATA_SUSPICIOUS_PATTERNS)


def is_suspicious_ip(ip: str) -> Tuple[bool, str]:
    """
    Check if IP matches known suspicious patterns.
    
    Args:
        ip: IP address to check
        
    Returns:
        (is_suspicious, reason) tuple
    """
    for pattern, reason in SUSPICIOUS_IP_PATTERNS:
        if ip.startswith(pattern):
            return True, reason
    
    return False, ""


def get_port_risk_info(port: int) -> Dict[str, any]:
    """
    Get risk information for a network port.
    
    Args:
        port: Port number
        
    Returns:
        Dict with 'description', 'techniques' keys, or empty dict if not high-risk
    """
    if port in HIGH_RISK_PORTS:
        service_name, techniques = HIGH_RISK_PORTS[port]
        return {
            'description': service_name,
            'techniques': techniques
        }
    
    return {}
