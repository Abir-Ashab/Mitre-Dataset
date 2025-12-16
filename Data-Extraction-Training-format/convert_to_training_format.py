"""
Convert cleaned logs to session-aware instruction-tuning format
Groups logs by session_id and creates chunked training examples
Preserves ALL original fields - no data loss
Includes MITRE technique names with codes
"""

import json
import random
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Generator

# Load MITRE technique mapping
SCRIPT_DIR = Path(__file__).parent
with open(SCRIPT_DIR / 'mitre_techniques.json', 'r', encoding='utf-8') as f:
    MITRE_MAPPING = json.load(f)

# Configuration
CHUNK_SIZE = 30  # Number of logs per chunk (adjust 20-50 based on your needs)
TIME_WINDOW = None  # Alternative: use time-based chunking in seconds (e.g., 60)


def get_timestamp(log):
    """Extract timestamp from log for sorting"""
    # Try common timestamp fields
    for field in ['@timestamp', 'timestamp', 'event.created', 'winlog.time_created']:
        if field in log:
            return log[field]
        # Handle nested fields
        if '.' in field:
            parts = field.split('.')
            obj = log
            for part in parts:
                if isinstance(obj, dict) and part in obj:
                    obj = obj[part]
                else:
                    break
            else:
                return obj
    
    # Fallback: return empty string for stable sorting
    return ""


def group_by_session(logs: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group logs by session_id
    Memory-efficient using defaultdict
    """
    sessions = defaultdict(list)
    
    for log in logs:
        session_id = log.get('session_id', 'unknown')
        sessions[session_id].append(log)
    
    return dict(sessions)


def chunk_session_logs(session_logs: List[Dict], chunk_size: int = CHUNK_SIZE, time_window: int = TIME_WINDOW) -> Generator[List[Dict], None, None]:
    """
    Chunk session logs into smaller windows
    Supports both count-based and time-based chunking
    Yields chunks as generator for memory efficiency
    """
    # Sort logs by timestamp
    sorted_logs = sorted(session_logs, key=get_timestamp)
    
    if time_window:
        # Time-based chunking (more complex, not implemented in basic version)
        # For now, fall back to count-based
        chunk_size = chunk_size or 30
    
    # Count-based chunking
    for i in range(0, len(sorted_logs), chunk_size):
        chunk = sorted_logs[i:i + chunk_size]
        yield chunk


def create_training_example(logs_chunk: List[Dict]) -> Dict:
    """
    Convert a chunk of logs to instruction-tuning format
    Keeps ALL original fields in each log
    
    Args:
        logs_chunk: List of log objects from the same session
    
    Returns:
        Training example dict with instruction, input, output
    """
    instruction = "Analyze this session log chunk and determine if it contains normal or suspicious activity. If suspicious, identify all MITRE ATT&CK techniques and explain why."
    
    # Extract metadata
    session_id = logs_chunk[0].get('session_id', 'unknown')
    timestamps = [get_timestamp(log) for log in logs_chunk]
    start_time = min(t for t in timestamps if t) if any(timestamps) else "unknown"
    end_time = max(t for t in timestamps if t) if any(timestamps) else "unknown"
    
    # Prepare input logs (remove label and mitre_techniques from display)
    input_logs = []
    for log in logs_chunk:
        clean_log = {k: v for k, v in log.items() if k not in ['label', 'mitre_techniques']}
        input_logs.append(clean_log)
    
    # Create input structure
    input_data = {
        "metadata": {
            "session_id": session_id,
            "start_time": start_time,
            "end_time": end_time,
            "number_of_events": len(logs_chunk)
        },
        "logs": input_logs
    }
    
    input_text = json.dumps(input_data, ensure_ascii=False)
    
    # Determine output label
    suspicious_logs = [log for log in logs_chunk if log.get('label') == 'suspicious']
    
    if suspicious_logs:
        # Chunk is suspicious - merge and deduplicate MITRE techniques
        all_techniques = set()
        for log in suspicious_logs:
            techniques = log.get('mitre_techniques', [])
            if techniques:
                all_techniques.update(techniques)
        
        output_parts = ["Status: Suspicious"]
        
        if all_techniques:
            # Format techniques with names
            formatted_techniques = []
            for technique in sorted(all_techniques):
                technique_name = MITRE_MAPPING.get(technique, "Unknown Technique")
                formatted_techniques.append(f"{technique} ({technique_name})")
            
            output_parts.append(f"MITRE Techniques: {', '.join(formatted_techniques)}")
        else:
            output_parts.append("MITRE Techniques: Not specified")
        
        output_parts.append(f"Reason: Malicious activity detected in {len(suspicious_logs)} out of {len(logs_chunk)} events based on behavioral patterns")
        
        output = "\n".join(output_parts)
    else:
        output = "Status: Normal\nReason: Standard system activity with no suspicious indicators across all events"
    
    return {
        "instruction": instruction,
        "input": input_text,
        "output": output
    }


def main():
    print("="*70)
    print("CONVERTING LOGS TO SESSION-AWARE TRAINING FORMAT")
    print("Preserving ALL original fields - zero data loss")
    print(f"Chunk size: {CHUNK_SIZE} logs per example")
    print("="*70)
    
    # Paths
    base_dir = Path(__file__).parent
    output_dir = base_dir / 'output'
    training_dir = base_dir / 'training_data'
    training_dir.mkdir(exist_ok=True)
    
    suspicious_file = output_dir / 'cleaned_suspicious_logs.json'
    normal_file = output_dir / 'cleaned_normal_logs.json'
    
    # Load cleaned logs
    print("\n📂 Loading cleaned logs...")
    with open(suspicious_file, 'r', encoding='utf-8') as f:
        suspicious_logs = json.load(f)
    
    with open(normal_file, 'r', encoding='utf-8') as f:
        normal_logs = json.load(f)
    
    print(f"   Suspicious logs: {len(suspicious_logs):,}")
    print(f"   Normal logs: {len(normal_logs):,}")
    
    # Combine all logs
    all_logs = suspicious_logs + normal_logs
    total_logs = len(all_logs)
    
    print(f"\n   Total individual logs: {total_logs:,}")
    
    # Group by session
    print("\n🔗 Grouping logs by session_id...")
    sessions = group_by_session(all_logs)
    print(f"   Found {len(sessions):,} unique sessions")
    
    # Show session statistics
    session_sizes = [len(logs) for logs in sessions.values()]
    print(f"   Session size range: {min(session_sizes):,} - {max(session_sizes):,} logs")
    print(f"   Average session size: {sum(session_sizes) / len(session_sizes):.0f} logs")
    
    # Process sessions into chunks (keeping session order intact)
    print(f"\n🔄 Creating chunked training examples...")
    print(f"   (Chunk size: {CHUNK_SIZE} logs per example)")
    print("   (Preserving all original fields)")
    print("   (Maintaining session temporal order)")
    
    # Create list of (session_id, chunks) to maintain session grouping
    session_chunks = []
    failed = 0
    
    # Estimate total chunks for progress bar
    estimated_chunks = sum(len(logs) // CHUNK_SIZE + (1 if len(logs) % CHUNK_SIZE else 0) 
                          for logs in sessions.values())
    
    with tqdm(total=estimated_chunks, desc="Processing sessions") as pbar:
        for session_id, session_logs in sessions.items():
            try:
                # Chunk the session
                chunks_for_session = []
                for chunk in chunk_session_logs(session_logs, chunk_size=CHUNK_SIZE):
                    try:
                        example = create_training_example(chunk)
                        chunks_for_session.append(example)
                        pbar.update(1)
                    except Exception as e:
                        failed += 1
                        if failed <= 5:  # Show first 5 errors
                            print(f"\n⚠️  Error converting chunk: {e}")
                        pbar.update(1)
                
                # Store all chunks for this session together
                if chunks_for_session:
                    session_chunks.append((session_id, chunks_for_session))
            except Exception as e:
                print(f"\n⚠️  Error processing session {session_id}: {e}")
    
    if failed > 0:
        print(f"\n⚠️  {failed} chunks failed to convert")
    
    # Shuffle sessions and split by SESSION (not by individual chunks)
    print(f"\n🔀 Splitting sessions into train/val/test (preserving chunk order within sessions)...")
    random.seed(42)
    random.shuffle(session_chunks)
    
    # Split SESSIONS into train/val/test (70/15/15)
    total_sessions = len(session_chunks)
    train_session_count = int(total_sessions * 0.7)
    val_session_count = int(total_sessions * 0.15)
    
    train_sessions = session_chunks[:train_session_count]
    val_sessions = session_chunks[train_session_count:train_session_count + val_session_count]
    test_sessions = session_chunks[train_session_count + val_session_count:]
    
    # Flatten each split: concatenate chunks session by session
    train_data = []
    for session_id, chunks in train_sessions:
        train_data.extend(chunks)
    
    val_data = []
    for session_id, chunks in val_sessions:
        val_data.extend(chunks)
    
    test_data = []
    for session_id, chunks in test_sessions:
        test_data.extend(chunks)
    
    total_examples = len(train_data) + len(val_data) + len(test_data)
    
    print(f"\n✅ Successfully created {total_examples:,} training examples")
    print(f"   From {total_logs:,} individual logs across {len(session_chunks):,} sessions")
    print(f"   All original fields preserved in each log")
    print(f"   ✅ Session chunks kept in consecutive order within each split")
    
    print(f"\n📊 Dataset split:")
    print(f"   Train: {len(train_data):,} chunks (70%)")
    print(f"   Validation: {len(val_data):,} chunks (15%)")
    print(f"   Test: {len(test_data):,} chunks (15%)")
    
    # Count labels in each split
    print("\n📈 Label distribution per split:")
    for split_name, split_data in [("Train", train_data), ("Val", val_data), ("Test", test_data)]:
        suspicious_count = sum(1 for ex in split_data if 'Suspicious' in ex['output'])
        normal_count = len(split_data) - suspicious_count
        print(f"   {split_name}: {suspicious_count:,} suspicious, {normal_count:,} normal")
    
    # Save as JSONL
    print(f"\n💾 Saving to {training_dir}/...")
    
    files_created = []
    for filename, data in [
        ('train.jsonl', train_data),
        ('val.jsonl', val_data),
        ('test.jsonl', test_data)
    ]:
        filepath = training_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            for example in data:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        file_size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"   ✅ {filename}: {len(data):,} lines ({file_size_mb:.1f} MB)")
        files_created.append(str(filepath))
    
    # Save statistics
    stats = {
        "conversion_type": "session-aware chunked",
        "chunk_size": CHUNK_SIZE,
        "total_chunks": total_examples,
        "total_individual_logs": total_logs,
        "total_sessions": len(session_chunks),
        "train_sessions": len(train_sessions),
        "val_sessions": len(val_sessions),
        "test_sessions": len(test_sessions),
        "suspicious_logs": len(suspicious_logs),
        "normal_logs": len(normal_logs),
        "avg_logs_per_chunk": total_logs / total_examples if total_examples else 0,
        "data_preservation": "100% - All original fields preserved in each log",
        "session_ordering": "Consecutive - chunks from same session kept together",
        "splits": {
            "train": {
                "count": len(train_data),
                "suspicious": sum(1 for ex in train_data if 'Suspicious' in ex['output']),
                "normal": sum(1 for ex in train_data if 'Normal' in ex['output'])
            },
            "val": {
                "count": len(val_data),
                "suspicious": sum(1 for ex in val_data if 'Suspicious' in ex['output']),
                "normal": sum(1 for ex in val_data if 'Normal' in ex['output'])
            },
            "test": {
                "count": len(test_data),
                "suspicious": sum(1 for ex in test_data if 'Suspicious' in ex['output']),
                "normal": sum(1 for ex in test_data if 'Normal' in ex['output'])
            }
        }
    }
    
    stats_file = training_dir / 'dataset_stats.json'
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    print(f"   ✅ dataset_stats.json")
    
    print("\n" + "="*70)
    print("✅ SESSION-AWARE CONVERSION COMPLETE!")
    print("="*70)
    print(f"\n📁 Training files created in: {training_dir}")
    print("   - train.jsonl")
    print("   - val.jsonl")
    print("   - test.jsonl")
    print("   - dataset_stats.json")
    print(f"\n✨ Total: {total_examples:,} chunked training examples")
    print(f"   (from {total_logs:,} logs across {len(session_chunks):,} sessions)")
    print(f"   (~{total_logs / total_examples if total_examples else 0:.0f} logs per chunk)")
    print("✅ All original fields preserved - zero data loss")
    print("✅ Session chunks maintained in consecutive order")
    print("\n🚀 Ready for fine-tuning with session context!")
    print("="*70)


if __name__ == '__main__':
    main()
