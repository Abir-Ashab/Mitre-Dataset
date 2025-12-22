"""
Utility functions shared across the pipeline
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any


def load_json_file(filepath: Path) -> Any:
    """
    Load JSON file with error handling
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Parsed JSON data
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error loading {filepath}: {e}")


def save_json_file(data: Any, filepath: Path, indent: int = 2):
    """
    Save data to JSON file
    
    Args:
        data: Data to save
        filepath: Path to save to
        indent: JSON indentation (default: 2)
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def get_log_signature(log: Dict) -> str:
    """
    Create a signature for the log based on all fields
    Used to identify exact duplicate objects
    
    Args:
        log: Log object
        
    Returns:
        MD5 hash signature
    """
    log_str = json.dumps(log, sort_keys=True)
    return hashlib.md5(log_str.encode()).hexdigest()


def get_timestamp(log: Dict) -> str:
    """
    Extract timestamp from log for sorting
    Tries common timestamp fields
    
    Args:
        log: Log object
        
    Returns:
        Timestamp string or empty string
    """
    # Try common timestamp fields
    timestamp_fields = [
        '@timestamp',
        'timestamp',
        'event.created',
        'winlog.time_created',
        'event_time',
        'created_at'
    ]
    
    for field in timestamp_fields:
        # Handle simple fields
        if field in log:
            return str(log[field])
        
        # Handle nested fields (e.g., 'event.created')
        if '.' in field:
            parts = field.split('.')
            obj = log
            try:
                for part in parts:
                    obj = obj[part]
                return str(obj)
            except (KeyError, TypeError):
                continue
    
    # Fallback: return empty string for stable sorting
    return ""


def print_stats(title: str, stats: Dict[str, Any]):
    """
    Print formatted statistics
    
    Args:
        title: Title for the stats section
        stats: Dictionary of statistics to print
    """
    print(f"\n{'='*70}")
    print(f"{title}")
    print('='*70)
    for key, value in stats.items():
        if isinstance(value, (int, float)):
            if isinstance(value, int):
                print(f"{key}: {value:,}")
            else:
                print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    print('='*70)


def count_logs_by_session(logs: List[Dict]) -> Dict[str, int]:
    """
    Count logs per session
    
    Args:
        logs: List of log objects
        
    Returns:
        Dictionary mapping session_id to count
    """
    from collections import defaultdict
    
    session_counts = defaultdict(int)
    for log in logs:
        session_id = log.get('session_id', 'unknown')
        session_counts[session_id] += 1
    
    return dict(session_counts)
