"""
Merge suspicious and normal chunks
Keeps ALL chunks without balancing/sampling
"""

import json
import random
from pathlib import Path
from typing import List, Dict

from config import (
    SUSPICIOUS_CHUNKS_FILE,
    NORMAL_CHUNKS_FILE,
    MERGED_CHUNKS_FILE
)


def load_chunks(filepath: Path) -> List[Dict]:
    """Load chunks from JSON file"""
    print(f"\n📂 Loading: {filepath.name}")
    with open(filepath, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"   Loaded {len(chunks):,} chunks")
    return chunks


def merge_all_chunks(suspicious_chunks: List[Dict], normal_chunks: List[Dict]) -> List[Dict]:
    """
    Merge all suspicious and normal chunks without balancing
    
    Args:
        suspicious_chunks: List of suspicious chunk objects
        normal_chunks: List of normal chunk objects
        
    Returns:
        Merged list of all chunks
    """
    print(f"\n🔗 Merging all chunks...")
    
    num_suspicious = len(suspicious_chunks)
    num_normal = len(normal_chunks)
    
    print(f"\n   Available:")
    print(f"   - Suspicious: {num_suspicious:,} chunks")
    print(f"   - Normal: {num_normal:,} chunks")
    
    # Label chunks for tracking
    for chunk in suspicious_chunks:
        chunk['chunk_label'] = 'suspicious'
    
    for chunk in normal_chunks:
        chunk['chunk_label'] = 'normal'
    
    # Combine all chunks and shuffle
    all_chunks = suspicious_chunks + normal_chunks
    random.seed(42)  # Reproducible shuffling
    random.shuffle(all_chunks)
    
    print(f"\n   ✅ Total merged chunks: {len(all_chunks):,}")
    print(f"   - Suspicious: {num_suspicious:,} ({num_suspicious/len(all_chunks)*100:.1f}%)")
    print(f"   - Normal: {num_normal:,} ({num_normal/len(all_chunks)*100:.1f}%)")
    
    return all_chunks


def save_chunks(chunks: List[Dict], filepath: Path):
    """Save chunks to JSON file"""
    print(f"\n💾 Saving to: {filepath}")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"   ✅ Saved {len(chunks):,} chunks")


def main():
    """Main function to merge all chunks"""
    print("="*70)
    print("MERGING ALL CHUNKS (NO BALANCING)")
    print("="*70)
    
    # Load chunks
    suspicious_chunks = load_chunks(SUSPICIOUS_CHUNKS_FILE)
    normal_chunks = load_chunks(NORMAL_CHUNKS_FILE)
    
    # Merge all chunks
    merged_chunks = merge_all_chunks(suspicious_chunks, normal_chunks)
    
    # Save merged chunks
    save_chunks(merged_chunks, MERGED_CHUNKS_FILE)
    
    # Print statistics
    print("\n" + "="*70)
    print("✅ MERGING COMPLETE")
    print("="*70)
    print(f"Output: {MERGED_CHUNKS_FILE}")
    print(f"Total chunks: {len(merged_chunks):,}")
    
    return merged_chunks


if __name__ == '__main__':
    main()
