"""
Clean extracted logs by removing duplicate objects only
Keeps ALL original fields intact - only removes duplicates
"""

import json
import hashlib
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict


def get_log_signature(log):
    """
    Create a signature for the log based on all important fields
    Used to identify exact duplicate objects
    """
    # Convert entire log to string and hash it
    # This identifies exact duplicates
    log_str = json.dumps(log, sort_keys=True)
    return hashlib.md5(log_str.encode()).hexdigest()


def clean_logs(input_file, output_file, label_type):
    """
    Clean logs by removing duplicate objects only
    Keeps all original fields
    
    Args:
        input_file: Path to extracted logs JSON
        output_file: Path to save cleaned logs
        label_type: 'suspicious' or 'normal'
    """
    print(f"\n{'='*70}")
    print(f"CLEANING {label_type.upper()} LOGS - REMOVING DUPLICATES ONLY")
    print('='*70)
    
    # Load logs
    print(f"\n📂 Loading from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    print(f"   Original count: {len(logs):,}")
    
    # Remove exact duplicates by signature
    print("\n🔍 Removing exact duplicate objects...")
    seen_signatures = set()
    unique_logs = []
    
    for log in tqdm(logs, desc="Deduplicating"):
        signature = get_log_signature(log)
        if signature not in seen_signatures:
            seen_signatures.add(signature)
            unique_logs.append(log)  # Keep original log with ALL fields
    
    duplicates_removed = len(logs) - len(unique_logs)
    print(f"   ✅ Removed {duplicates_removed:,} exact duplicates")
    print(f"   Remaining: {len(unique_logs):,}")
    
    # Sample if normal logs are too many
    final_logs = unique_logs
    if label_type == 'normal' and len(unique_logs) > 100000:
        print("\n⚖️  Sampling to reduce normal log size...")
        
        import random
        random.seed(42)
        final_logs = random.sample(unique_logs, 100000)
        print(f"   ✅ Sampled down to {len(final_logs):,} logs")
    
    # Save cleaned logs
    print(f"\n💾 Saving to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_logs, f, indent=2)
    
    # Statistics
    print(f"\n{'='*70}")
    print(f"✅ CLEANING COMPLETE")
    print('='*70)
    print(f"Original logs: {len(logs):,}")
    print(f"Duplicates removed: {duplicates_removed:,}")
    print(f"Final unique logs: {len(final_logs):,}")
    print(f"Reduction: {(1 - len(final_logs)/len(logs))*100:.1f}%")
    print(f"All original fields preserved ✓")
    print('='*70)
    
    return final_logs


def main():
    print("="*70)
    print("LOG DEDUPLICATION PIPELINE")
    print("="*70)
    
    base_dir = Path(__file__).parent
    output_dir = base_dir / 'output'
    
    # Clean suspicious logs
    suspicious_input = output_dir / 'extracted_suspicious_logs.json'
    suspicious_output = output_dir / 'cleaned_suspicious_logs.json'
    
    if suspicious_input.exists():
        clean_logs(suspicious_input, suspicious_output, 'suspicious')
    else:
        print(f"⚠️  {suspicious_input} not found!")
    
    # Clean normal logs
    normal_input = output_dir / 'extracted_normal_logs.json'
    normal_output = output_dir / 'cleaned_normal_logs.json'
    
    if normal_input.exists():
        clean_logs(normal_input, normal_output, 'normal')
    else:
        print(f"⚠️  {normal_input} not found!")
    
    print("\n" + "="*70)
    print("🎉 ALL LOGS CLEANED!")
    print("="*70)
    print("\n📁 Cleaned files:")
    print(f"   - {suspicious_output}")
    print(f"   - {normal_output}")
    print("\n🚀 Next: Run convert_to_training_format.py")
    print("="*70)


if __name__ == '__main__':
    main()
