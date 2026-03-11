"""
Normal behavior patterns for baseline comparison.

Defines expected/legitimate system activity patterns.
Helps teach the model what normal looks like (as important as suspicious patterns).
"""

from typing import Set, List, Tuple, Dict

# ============================================================================
# NORMAL PROCESSES
# ============================================================================

LEGITIMATE_PROCESSES: Set[str] = {
    'explorer.exe',
    'svchost.exe',
    'services.exe',
    'lsass.exe',
    'csrss.exe',
    'smss.exe',
    'winlogon.exe',
    'dwm.exe',
    'chrome.exe',
    'firefox.exe',
    'msedge.exe',
    'outlook.exe',
    'excel.exe',
    'word.exe',
    'teams.exe',
    'slack.exe',
}

# Trusted process paths
TRUSTED_PATHS: List[str] = [
    r'C:\Windows\System32',
    r'C:\Windows\SysWOW64',
    r'C:\Program Files',
    r'C:\Program Files (x86)',
]


# ============================================================================
# NORMAL NETWORK PATTERNS
# ============================================================================

# Standard ports for legitimate traffic
STANDARD_PORTS: Dict[int, str] = {
    80: 'HTTP - Web browsing',
    443: 'HTTPS - Secure web browsing',
    53: 'DNS - Name resolution',
    123: 'NTP - Time synchronization',
    25: 'SMTP - Email sending',
    110: 'POP3 - Email retrieval',
    143: 'IMAP - Email access',
    587: 'SMTP Submission',
    993: 'IMAPS - Secure email',
    995: 'POP3S - Secure email',
}

# Internal network ranges (RFC1918 private addresses)
INTERNAL_IP_RANGES: List[str] = [
    '10.',
    '192.168.',
    '172.16.', '172.17.', '172.18.', '172.19.',
    '172.20.', '172.21.', '172.22.', '172.23.',
    '172.24.', '172.25.', '172.26.', '172.27.',
    '172.28.', '172.29.', '172.30.', '172.31.',
    '127.',  # Localhost
]

# Trusted cloud services
TRUSTED_SERVICES: Dict[str, List[str]] = {
    'Microsoft': ['microsoft.com', 'office.com', 'office365.com', 'outlook.com', 'live.com', 'azure.com'],
    'Google': ['google.com', 'gmail.com', 'drive.google.com', 'docs.google.com'],
    'CDNs': ['cloudflare.com', 'akamai.com', 'fastly.com'],
    'Updates': ['windows.com', 'update.microsoft.com', 'adobe.com'],
}


# ============================================================================
# NORMAL LOGON PATTERNS
# ============================================================================

LOGON_TYPES: Dict[int, Tuple[str, str]] = {
    # (logon_type: (name, typical_usage))
    2: ('Interactive', 'User console login - normal desktop/laptop login'),
    3: ('Network', 'Network share access - accessing file shares or printers'),
    4: ('Batch', 'Scheduled task - automated tasks'),
    5: ('Service', 'Windows service - legitimate service accounts'),
    7: ('Unlock', 'Screen unlock - user returning to workstation'),
    10: ('RemoteInteractive', 'RDP or Terminal Services - if authorized'),
    11: ('CachedInteractive', 'Cached credentials - offline login'),
}

# Business hours (used for timing analysis)
BUSINESS_HOURS: Tuple[int, int] = (8, 18)  # 8 AM to 6 PM
BUSINESS_DAYS: List[int] = [0, 1, 2, 3, 4]  # Monday=0 to Friday=4


# ============================================================================
# NORMAL REGISTRY ACTIVITY
# ============================================================================

NORMAL_REGISTRY_PATTERNS: List[Tuple[str, str]] = [
    # (path_pattern, description)
    ('HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Installer', 'Software installation'),
    ('HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer', 'Explorer settings'),
    ('HKLM\\System\\CurrentControlSet\\Services', 'Service configuration'),
    ('HKCU\\Software\\Microsoft\\Office', 'Office application settings'),
]


# ============================================================================
# NORMAL FILE OPERATIONS
# ============================================================================

# File extensions typically accessed during normal use
NORMAL_FILE_EXTENSIONS: Set[str] = {
    '.txt', '.doc', '.docx', '.pdf', '.xlsx', '.pptx',
    '.jpg', '.png', '.gif', '.mp4', '.mp3',
    '.html', '.css', '.js',
}

# System directories (readonly for most users)
SYSTEM_DIRECTORIES: List[str] = [
    r'C:\Windows\System32',
    r'C:\Windows\SysWOW64',
    r'C:\Program Files',
    r'C:\ProgramData',
]


# ============================================================================
# BASELINE THRESHOLDS
# ============================================================================

BASELINE_THRESHOLDS: Dict[str, int] = {
    'normal_process_spawns_per_min': 5,
    'normal_network_connections_per_min': 20,
    'normal_file_operations_per_min': 10,
    'normal_registry_changes_per_min': 5,
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_internal_ip(ip: str) -> bool:
    """
    Check if IP is in internal/private range.
    
    Args:
        ip: IP address to check
        
    Returns:
        True if internal IP
    """
    return any(ip.startswith(prefix) for prefix in INTERNAL_IP_RANGES)


def is_standard_port(port: int) -> Tuple[bool, str]:
    """
    Check if port is standard/expected.
    
    Args:
        port: Port number
        
    Returns:
        (is_standard, description) tuple
    """
    if port in STANDARD_PORTS:
        return True, STANDARD_PORTS[port]
    return False, ""


def is_legitimate_process(process_name: str, process_path: str = "") -> Tuple[bool, str]:
    """
    Check if process is known legitimate.
    
    Args:
        process_name: Process executable name
        process_path: Full path to executable
        
    Returns:
        (is_legitimate, reason) tuple
    """
    if not process_name:
        return False, ""
    
    process_lower = process_name.lower()
    
    # Check against known legitimate processes
    if process_lower in LEGITIMATE_PROCESSES:
        return True, f"Known legitimate: {process_name}"
    
    # Check if from trusted path
    if process_path:
        for trusted_path in TRUSTED_PATHS:
            if process_path.startswith(trusted_path):
                return True, f"From trusted directory: {trusted_path}"
    
    return False, ""


def get_logon_type_info(logon_type: int) -> Tuple[str, str]:
    """
    Get information about logon type.
    
    Args:
        logon_type: Windows logon type number
        
    Returns:
        (name, description) tuple
    """
    if logon_type in LOGON_TYPES:
        return LOGON_TYPES[logon_type]
    return ("Unknown", f"LogonType {logon_type}")


def is_business_hours(timestamp: str) -> bool:
    """
    Check if timestamp falls within business hours.
    
    Args:
        timestamp: ISO format timestamp
        
    Returns:
        True if within business hours
    """
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return (dt.weekday() in BUSINESS_DAYS and 
                BUSINESS_HOURS[0] <= dt.hour < BUSINESS_HOURS[1])
    except:
        return False  # Cannot determine, assume not business hours
