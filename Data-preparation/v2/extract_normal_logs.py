"""
Extract normal logs from normal-logs directory (Pseudo-Annotated-Logs)
Processes each session folder and extracts all logs (assumed to be normal)
"""

import json
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict, Tuple

from config import NORMAL_LOGS_DIR, EXTRACTED_NORMAL_FILE
from utils import load_json_file, save_json_file, print_stats


def extract_normal_logs(logs_dir: Path) -> Tuple[List[Dict], Dict]:
    """
    Extract all normal logs from session folders
    Assumes all logs in normal-logs directory are normal (no label filtering needed)
    
    Args:
        logs_dir: Path to normal-logs directory
        
    Returns:
        Tuple of (extracted_logs, session_stats)
    """
    # Get all session folders
    session_folders = sorted([f for f in logs_dir.iterdir() if f.is_dir()])
    
    print(f"\n🔍 Scanning: {logs_dir}")
    print(f"   Found {len(session_folders)} session folders")
    
    extracted_logs = []
    session_stats = {}
    
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
            
            # Extract all logs (they're all normal in this directory)
            for log in data.get('logs', []):
                # Add session_id to each log for tracking
                log['session_id'] = session_id
                # Ensure label is set to 'normal'
                log['label'] = 'normal'
                extracted_logs.append(log)
                session_count += 1
            
            session_stats[session_id] = session_count
            
        except Exception as e:
            print(f"   ❌ Error processing {folder.name}: {e}")
    
    return extracted_logs, session_stats


def main():
    """Main function to extract normal logs"""
    print("="*70)
    print("EXTRACTING NORMAL LOGS")
    print("="*70)
    
    # Validate paths
    if not NORMAL_LOGS_DIR.exists():
        print(f"❌ Error: Normal logs directory not found: {NORMAL_LOGS_DIR}")
        return
    
    # Extract logs
    extracted_logs, session_stats = extract_normal_logs(NORMAL_LOGS_DIR)
    
    # Save extracted logs
    save_json_file(extracted_logs, EXTRACTED_NORMAL_FILE)
    
    # Print statistics
    stats = {
        "Total sessions processed": len(session_stats),
        "Total normal logs extracted": len(extracted_logs),
        "Output file": str(EXTRACTED_NORMAL_FILE)
    }
    
    print_stats("✅ EXTRACTION COMPLETE", stats)
    
    if session_stats:
        print("\n📊 Normal logs per session:")
        for session_id, count in sorted(session_stats.items()):
            print(f"   {session_id}: {count:,}")
    
    return extracted_logs, session_stats


if __name__ == '__main__':
    main()
