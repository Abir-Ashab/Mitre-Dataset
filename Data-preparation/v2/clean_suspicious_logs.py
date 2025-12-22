"""
Clean suspicious logs by removing exact duplicates
Preserves all original fields - only deduplicates
"""

from tqdm import tqdm
from typing import List, Dict

from config import EXTRACTED_SUSPICIOUS_FILE, CLEANED_SUSPICIOUS_FILE
from utils import load_json_file, save_json_file, get_log_signature, print_stats


def deduplicate_logs(logs: List[Dict]) -> List[Dict]:
    """
    Remove exact duplicate logs based on signature
    Keeps all original fields
    
    Args:
        logs: List of log objects
        
    Returns:
        Deduplicated list of logs
    """
    print("\n🔍 Removing exact duplicates...")
    
    seen_signatures = set()
    unique_logs = []
    
    for log in tqdm(logs, desc="   Deduplicating"):
        signature = get_log_signature(log)
        if signature not in seen_signatures:
            seen_signatures.add(signature)
            unique_logs.append(log)
    
    duplicates_removed = len(logs) - len(unique_logs)
    print(f"   ✅ Removed {duplicates_removed:,} exact duplicates")
    
    return unique_logs


def main():
    """Main function to clean suspicious logs"""
    print("="*70)
    print("CLEANING SUSPICIOUS LOGS")
    print("="*70)
    
    # Load extracted logs
    print(f"\n📂 Loading from: {EXTRACTED_SUSPICIOUS_FILE}")
    logs = load_json_file(EXTRACTED_SUSPICIOUS_FILE)
    print(f"   Original count: {len(logs):,}")
    
    # Deduplicate
    unique_logs = deduplicate_logs(logs)
    
    # Save cleaned logs
    print(f"\n💾 Saving to: {CLEANED_SUSPICIOUS_FILE}")
    save_json_file(unique_logs, CLEANED_SUSPICIOUS_FILE)
    
    # Print statistics
    stats = {
        "Original logs": len(logs),
        "Duplicates removed": len(logs) - len(unique_logs),
        "Unique logs remaining": len(unique_logs),
        "Deduplication rate": f"{((len(logs) - len(unique_logs)) / len(logs) * 100):.2f}%" if logs else "0%",
        "Output file": str(CLEANED_SUSPICIOUS_FILE)
    }
    
    print_stats("✅ CLEANING COMPLETE", stats)
    
    return unique_logs


if __name__ == '__main__':
    main()
