"""
Extract suspicious logs from suspicious-logs directory
Processes each session folder and extracts only suspicious-labeled logs
"""

import json
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict, Tuple

from config import SUSPICIOUS_LOGS_DIR, EXTRACTED_SUSPICIOUS_FILE
from utils import load_json_file, save_json_file, print_stats


def extract_suspicious_logs(logs_dir: Path) -> Tuple[List[Dict], Dict]:
    """
    Extract all suspicious logs from session folders
    
    Args:
        logs_dir: Path to suspicious-logs directory
        
    Returns:
        Tuple of (extracted_logs, session_stats)
    """
    # Get all session folders
    session_folders = sorted([f for f in logs_dir.iterdir() if f.is_dir()])
    
    print(f"\n🔍 Scanning: {logs_dir}")
    print(f"   Found {len(session_folders)} session folders")
    
    extracted_logs = []
    session_stats = {}
    sessions_with_suspicious = 0
    sessions_without_suspicious = 0
    
    # Process each session
    for folder in tqdm(session_folders, desc="📦 Processing sessions"):
        json_files = list(folder.glob("*.json"))
        
        if not json_files:
            print(f"   ⚠️  No JSON file in {folder.name}")
            continue
        
        try:
            data = load_json_file(json_files[0])
            
            session_id = data.get('session_id', folder.name)
            session_count = 0
            
            # Extract logs with 'suspicious' label
            for log in data.get('logs', []):
                if log.get('label') == 'suspicious':
                    # Add session_id to each log for tracking
                    log['session_id'] = session_id
                    extracted_logs.append(log)
                    session_count += 1
            
            # Track statistics
            if session_count > 0:
                sessions_with_suspicious += 1
                session_stats[session_id] = session_count
            else:
                sessions_without_suspicious += 1
            
        except Exception as e:
            print(f"   ❌ Error processing {folder.name}: {e}")
    
    return extracted_logs, session_stats, sessions_with_suspicious, sessions_without_suspicious


def main():
    """Main function to extract suspicious logs"""
    print("="*70)
    print("EXTRACTING SUSPICIOUS LOGS")
    print("="*70)
    
    # Validate paths
    if not SUSPICIOUS_LOGS_DIR.exists():
        print(f"❌ Error: Suspicious logs directory not found: {SUSPICIOUS_LOGS_DIR}")
        return
    
    # Extract logs
    extracted_logs, session_stats, with_sus, without_sus = extract_suspicious_logs(SUSPICIOUS_LOGS_DIR)
    
    # Save extracted logs
    save_json_file(extracted_logs, EXTRACTED_SUSPICIOUS_FILE)
    
    # Print statistics
    stats = {
        "Total sessions scanned": with_sus + without_sus,
        "Sessions with suspicious logs": with_sus,
        "Sessions without suspicious logs": without_sus,
        "Total suspicious logs extracted": len(extracted_logs),
        "Output file": str(EXTRACTED_SUSPICIOUS_FILE)
    }
    
    print_stats("✅ EXTRACTION COMPLETE", stats)
    
    if session_stats:
        print("\n📊 Suspicious logs per session:")
        for session_id, count in sorted(session_stats.items()):
            print(f"   {session_id}: {count:,}")
    
    return extracted_logs, session_stats


if __name__ == '__main__':
    main()
