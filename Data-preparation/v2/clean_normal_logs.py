"""
Clean normal logs by removing exact duplicates
Preserves all original fields - only deduplicates
Optionally samples down if too many logs
"""

import random
from tqdm import tqdm
from typing import List, Dict

from config import EXTRACTED_NORMAL_FILE, CLEANED_NORMAL_FILE
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


def sample_logs(logs: List[Dict], max_logs: int = 100000) -> List[Dict]:
    """
    Sample logs if count exceeds threshold
    
    Args:
        logs: List of log objects
        max_logs: Maximum number of logs to keep
        
    Returns:
        Sampled list of logs
    """
    if len(logs) <= max_logs:
        return logs
    
    print(f"\n⚖️  Sampling to reduce dataset size...")
    print(f"   Original: {len(logs):,} logs")
    print(f"   Target: {max_logs:,} logs")
    
    random.seed(42)  # Reproducible sampling
    sampled = random.sample(logs, max_logs)
    
    print(f"   ✅ Sampled down to {len(sampled):,} logs")
    
    return sampled


def main():
    """Main function to clean normal logs"""
    print("="*70)
    print("CLEANING NORMAL LOGS")
    print("="*70)
    
    # Load extracted logs
    print(f"\n📂 Loading from: {EXTRACTED_NORMAL_FILE}")
    logs = load_json_file(EXTRACTED_NORMAL_FILE)
    print(f"   Original count: {len(logs):,}")
    
    # Deduplicate
    unique_logs = deduplicate_logs(logs)
    
    # Optional: Sample if too many (can be disabled/adjusted)
    # Uncomment the line below if you want to limit normal logs
    # unique_logs = sample_logs(unique_logs, max_logs=100000)
    
    # Save cleaned logs
    print(f"\n💾 Saving to: {CLEANED_NORMAL_FILE}")
    save_json_file(unique_logs, CLEANED_NORMAL_FILE)
    
    # Print statistics
    stats = {
        "Original logs": len(logs),
        "Duplicates removed": len(logs) - len(unique_logs),
        "Unique logs remaining": len(unique_logs),
        "Deduplication rate": f"{((len(logs) - len(unique_logs)) / len(logs) * 100):.2f}%" if logs else "0%",
        "Output file": str(CLEANED_NORMAL_FILE)
    }
    
    print_stats("✅ CLEANING COMPLETE", stats)
    
    return unique_logs


if __name__ == '__main__':
    main()
