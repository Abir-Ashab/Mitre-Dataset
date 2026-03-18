"""
Split training examples into train/val/test sets
Ensures session-based splitting (all chunks from same session stay together)
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

from config import (
    MERGED_CHUNKS_FILE,
    TRAIN_FILE,
    VAL_FILE,
    TEST_FILE,
    TRAIN_SPLIT,
    VAL_SPLIT,
    TEST_SPLIT,
    FINAL_OUTPUT_DIR,
    load_mitre_mapping,
    INSTRUCTION_TEMPLATE
)

# Import the NEW modular conversion function
from convert_to_training_format import create_training_example


# OLD template-based conversion removed - now using the new modular system
# The new create_training_example() provides field-specific analysis


def group_chunks_by_session(chunks: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group chunks by session_id
    
    Args:
        chunks: List of chunk objects
        
    Returns:
        Dictionary mapping session_id to list of chunks
    """
    sessions = defaultdict(list)
    
    for chunk in chunks:
        session_id = chunk.get('metadata', {}).get('session_id', 'unknown')
        sessions[session_id].append(chunk)
    
    return dict(sessions)


def split_by_session_chunk_based(chunks: List[Dict], train_ratio: float, val_ratio: float, test_ratio: float) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Split chunks into train/val/test by session, but aiming for target CHUNK counts
    All chunks from same session stay together
    Uses bin packing approach to achieve target chunk distribution
    
    Args:
        chunks: List of chunk objects
        train_ratio: Ratio for training set (based on chunk count, not session count)
        val_ratio: Ratio for validation set
        test_ratio: Ratio for test set
        
    Returns:
        Tuple of (train_chunks, val_chunks, test_chunks)
    """
    # Group by session
    sessions = group_chunks_by_session(chunks)
    
    # Calculate target chunk counts
    total_chunks = len(chunks)
    target_train = int(total_chunks * train_ratio)
    target_val = int(total_chunks * val_ratio)
    target_test = int(total_chunks * test_ratio)
    
    # Create list of (session_id, chunk_count) and sort by chunk count descending
    # This helps with bin packing - assign large sessions first
    session_info = [(sid, len(schunks)) for sid, schunks in sessions.items()]
    session_info.sort(key=lambda x: x[1], reverse=True)
    
    # Initialize splits
    train_sessions = []
    val_sessions = []
    test_sessions = []
    
    train_chunk_count = 0
    val_chunk_count = 0
    test_chunk_count = 0
    
    # Assign each session to the split with most room (closest to target)
    for session_id, chunk_count in session_info:
        # Calculate how much each split needs to reach its target
        train_deficit = target_train - train_chunk_count
        val_deficit = target_val - val_chunk_count
        test_deficit = target_test - test_chunk_count
        
        # Assign to split with largest deficit (most need)
        if train_deficit >= val_deficit and train_deficit >= test_deficit and train_deficit > 0:
            train_sessions.append(session_id)
            train_chunk_count += chunk_count
        elif val_deficit >= test_deficit and val_deficit > 0:
            val_sessions.append(session_id)
            val_chunk_count += chunk_count
        else:
            test_sessions.append(session_id)
            test_chunk_count += chunk_count
    
    # Collect chunks for each split
    train_chunks = []
    val_chunks = []
    test_chunks = []
    
    for session_id in train_sessions:
        train_chunks.extend(sessions[session_id])
    
    for session_id in val_sessions:
        val_chunks.extend(sessions[session_id])
    
    for session_id in test_sessions:
        test_chunks.extend(sessions[session_id])
    
    # Shuffle chunks within each split
    random.seed(42)
    random.shuffle(train_chunks)
    random.shuffle(val_chunks)
    random.shuffle(test_chunks)
    
    return train_chunks, val_chunks, test_chunks


def split_by_label_and_session(chunks: List[Dict], train_ratio: float, val_ratio: float, test_ratio: float) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Split chunks into train/val/test, ensuring both suspicious and normal
    chunks are split with the same ratio separately
    
    Args:
        chunks: List of chunk objects
        train_ratio: Ratio for training set
        val_ratio: Ratio for validation set
        test_ratio: Ratio for test set
        
    Returns:
        Tuple of (train_chunks, val_chunks, test_chunks)
    """
    print("\n[*] Splitting by label and session...")
    
    # Separate suspicious and normal chunks
    suspicious_chunks = [c for c in chunks if c.get('chunk_label') == 'suspicious']
    normal_chunks = [c for c in chunks if c.get('chunk_label') == 'normal']
    
    print(f"   Total chunks: {len(chunks):,}")
    print(f"   - Suspicious: {len(suspicious_chunks):,}")
    print(f"   - Normal: {len(normal_chunks):,}")
    
    # Split suspicious chunks by session (chunk-count based)
    print("\n   Splitting SUSPICIOUS chunks by session (chunk-count based):")
    sus_sessions = group_chunks_by_session(suspicious_chunks)
    print(f"   - Sessions: {len(sus_sessions):,}")
    print(f"   - Target: {train_ratio*100:.0f}% train, {val_ratio*100:.0f}% val, {test_ratio*100:.0f}% test (by chunk count)")
    sus_train, sus_val, sus_test = split_by_session_chunk_based(suspicious_chunks, train_ratio, val_ratio, test_ratio)
    print(f"   - Train: {len(sus_train):,} chunks ({len(sus_train)/len(suspicious_chunks)*100:.1f}%)")
    print(f"   - Val:   {len(sus_val):,} chunks ({len(sus_val)/len(suspicious_chunks)*100:.1f}%)")
    print(f"   - Test:  {len(sus_test):,} chunks ({len(sus_test)/len(suspicious_chunks)*100:.1f}%)")
    
    # Split normal chunks by session (chunk-count based)
    print("\n   Splitting NORMAL chunks by session (chunk-count based):")
    norm_sessions = group_chunks_by_session(normal_chunks)
    print(f"   - Sessions: {len(norm_sessions):,}")
    print(f"   - Target: {train_ratio*100:.0f}% train, {val_ratio*100:.0f}% val, {test_ratio*100:.0f}% test (by chunk count)")
    norm_train, norm_val, norm_test = split_by_session_chunk_based(normal_chunks, train_ratio, val_ratio, test_ratio)
    print(f"   - Train: {len(norm_train):,} chunks ({len(norm_train)/len(normal_chunks)*100:.1f}%)")
    print(f"   - Val:   {len(norm_val):,} chunks ({len(norm_val)/len(normal_chunks)*100:.1f}%)")
    print(f"   - Test:  {len(norm_test):,} chunks ({len(norm_test)/len(normal_chunks)*100:.1f}%)")
    
    # Combine splits
    train_chunks = sus_train + norm_train
    val_chunks = sus_val + norm_val
    test_chunks = sus_test + norm_test
    
    # Shuffle combined splits
    random.shuffle(train_chunks)
    random.shuffle(val_chunks)
    random.shuffle(test_chunks)
    
    print(f"\n   [*] Final split results:")
    print(f"   - Train: {len(train_chunks):,} chunks ({len(train_chunks)/len(chunks)*100:.1f}%)")
    print(f"     • Suspicious: {len(sus_train):,} ({len(sus_train)/len(train_chunks)*100:.1f}%)")
    print(f"     • Normal: {len(norm_train):,} ({len(norm_train)/len(train_chunks)*100:.1f}%)")
    print(f"   - Val:   {len(val_chunks):,} chunks ({len(val_chunks)/len(chunks)*100:.1f}%)")
    print(f"     • Suspicious: {len(sus_val):,} ({len(sus_val)/len(val_chunks)*100:.1f}%)")
    print(f"     • Normal: {len(norm_val):,} ({len(norm_val)/len(val_chunks)*100:.1f}%)")
    print(f"   - Test:  {len(test_chunks):,} chunks ({len(test_chunks)/len(chunks)*100:.1f}%)")
    print(f"     • Suspicious: {len(sus_test):,} ({len(sus_test)/len(test_chunks)*100:.1f}%)")
    print(f"     • Normal: {len(norm_test):,} ({len(norm_test)/len(test_chunks)*100:.1f}%)")
    
    return train_chunks, val_chunks, test_chunks


def save_training_examples(examples: List[Dict], filepath: Path):
    """Save training examples to JSONL file (one JSON object per line)"""
    with open(filepath, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    file_size_mb = filepath.stat().st_size / (1024 * 1024)
    print(f"   [+] Saved to: {filepath} ({len(examples):,} lines, {file_size_mb:.1f} MB)")


def main():
    """Main function to split data into train/val/test"""
    print("="*70)
    print("SPLITTING INTO TRAIN/VAL/TEST SETS")
    print(f"Split ratio: {TRAIN_SPLIT*100:.0f}% train, {VAL_SPLIT*100:.0f}% val, {TEST_SPLIT*100:.0f}% test")
    print("(Suspicious and normal chunks split separately)")
    print("="*70)
    
    # Load merged chunks
    print("\n[*] Loading: {}".format(MERGED_CHUNKS_FILE))
    with open(MERGED_CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"   Loaded {len(chunks):,} chunks")
    
    # Split by label and session (ensures 80/10/10 for both suspicious and normal)
    train_chunks, val_chunks, test_chunks = split_by_label_and_session(
        chunks, TRAIN_SPLIT, VAL_SPLIT, TEST_SPLIT
    )
    
    # Load MITRE mapping
    print("\n🔄 Converting to training format...")
    mitre_mapping = load_mitre_mapping()
    
    # Convert each split to training format
    train_examples = [create_training_example(chunk, mitre_mapping) for chunk in train_chunks]
    val_examples = [create_training_example(chunk, mitre_mapping) for chunk in val_chunks]
    test_examples = [create_training_example(chunk, mitre_mapping) for chunk in test_chunks]
    
    # Save splits
    print("\n[*] Saving splits...")
    save_training_examples(train_examples, TRAIN_FILE)
    save_training_examples(val_examples, VAL_FILE)
    save_training_examples(test_examples, TEST_FILE)
    
    # Print statistics
    print("\n" + "="*70)
    print("[+] SPLITTING COMPLETE")
    print("="*70)
    print(f"Train: {len(train_examples):,} examples")
    print(f"Val:   {len(val_examples):,} examples")
    print(f"Test:  {len(test_examples):,} examples")
    print(f"Total: {len(train_examples) + len(val_examples) + len(test_examples):,} examples")
    print(f"\n📁 Output format: JSONL (one example per line)")
    print(f"📁 Output directory: {FINAL_OUTPUT_DIR}")
    
    return train_examples, val_examples, test_examples


if __name__ == '__main__':
    main()
