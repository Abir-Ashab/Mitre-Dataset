"""
Create chunks from cleaned suspicious logs
Groups by session_id and creates fixed-size chunks (20 logs each)
Skips sessions/chunks with no suspicious logs
"""

from collections import defaultdict
from typing import List, Dict, Tuple
from tqdm import tqdm

from config import CLEANED_SUSPICIOUS_FILE, SUSPICIOUS_CHUNKS_FILE, CHUNK_SIZE, MIN_CHUNK_SIZE
from utils import load_json_file, save_json_file, get_timestamp, print_stats


def group_by_session(logs: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group logs by session_id
    
    Args:
        logs: List of log objects
        
    Returns:
        Dictionary mapping session_id to list of logs
    """
    sessions = defaultdict(list)
    
    for log in logs:
        session_id = log.get('session_id', 'unknown')
        sessions[session_id].append(log)
    
    return dict(sessions)


def create_chunks(session_logs: List[Dict], chunk_size: int = CHUNK_SIZE) -> List[List[Dict]]:
    """
    Create fixed-size chunks from session logs
    Chunks are sorted by timestamp
    
    Args:
        session_logs: List of logs from same session
        chunk_size: Number of logs per chunk
        
    Returns:
        List of chunks (each chunk is a list of logs)
    """
    # Sort by timestamp
    sorted_logs = sorted(session_logs, key=get_timestamp)
    
    chunks = []
    for i in range(0, len(sorted_logs), chunk_size):
        chunk = sorted_logs[i:i + chunk_size]
        
        # Only include chunks that meet minimum size or are the last chunk
        if len(chunk) >= MIN_CHUNK_SIZE or i + chunk_size >= len(sorted_logs):
            chunks.append(chunk)
    
    return chunks


def create_chunk_metadata(chunk: List[Dict], chunk_index: int, session_id: str) -> Dict:
    """
    Create metadata for a chunk
    
    Args:
        chunk: List of logs in the chunk
        chunk_index: Index of this chunk in the session
        session_id: Session identifier
        
    Returns:
        Metadata dictionary
    """
    timestamps = [get_timestamp(log) for log in chunk]
    valid_timestamps = [t for t in timestamps if t]
    
    metadata = {
        "session_id": session_id,
        "chunk_index": chunk_index,
        "chunk_size": len(chunk),
        "start_time": min(valid_timestamps) if valid_timestamps else "unknown",
        "end_time": max(valid_timestamps) if valid_timestamps else "unknown"
    }
    
    return metadata


def main():
    """Main function to create suspicious log chunks"""
    print("="*70)
    print("CREATING SUSPICIOUS LOG CHUNKS")
    print(f"Chunk size: {CHUNK_SIZE} logs")
    print(f"Minimum chunk size: {MIN_CHUNK_SIZE} logs")
    print("="*70)
    
    # Load cleaned logs
    print(f"\n📂 Loading from: {CLEANED_SUSPICIOUS_FILE}")
    logs = load_json_file(CLEANED_SUSPICIOUS_FILE)
    print(f"   Total logs: {len(logs):,}")
    
    # Group by session
    print("\n🔗 Grouping logs by session_id...")
    sessions = group_by_session(logs)
    print(f"   Found {len(sessions):,} unique sessions")
    
    # Show session statistics
    session_sizes = [len(session_logs) for session_logs in sessions.values()]
    if session_sizes:
        print(f"   Session size range: {min(session_sizes):,} - {max(session_sizes):,} logs")
        print(f"   Average session size: {sum(session_sizes) / len(session_sizes):.1f} logs")
    
    # Create chunks for each session
    print("\n✂️  Creating chunks...")
    all_chunks = []
    chunk_stats = {
        'total_chunks': 0,
        'total_sessions': len(sessions),
        'sessions_with_chunks': 0,
        'chunks_per_session': []
    }
    
    for session_id, session_logs in tqdm(sessions.items(), desc="   Processing sessions"):
        # Create chunks for this session
        chunks = create_chunks(session_logs, CHUNK_SIZE)
        
        if chunks:
            chunk_stats['sessions_with_chunks'] += 1
            chunk_stats['chunks_per_session'].append(len(chunks))
        
        # Add metadata and store each chunk
        for idx, chunk in enumerate(chunks):
            metadata = create_chunk_metadata(chunk, idx, session_id)
            
            chunk_data = {
                "metadata": metadata,
                "logs": chunk
            }
            
            all_chunks.append(chunk_data)
            chunk_stats['total_chunks'] += 1
    
    # Save chunks
    print(f"\n💾 Saving to: {SUSPICIOUS_CHUNKS_FILE}")
    save_json_file(all_chunks, SUSPICIOUS_CHUNKS_FILE)
    
    # Print statistics
    avg_chunks = sum(chunk_stats['chunks_per_session']) / len(chunk_stats['chunks_per_session']) if chunk_stats['chunks_per_session'] else 0
    
    stats = {
        "Total input logs": len(logs),
        "Total sessions": chunk_stats['total_sessions'],
        "Sessions with chunks": chunk_stats['sessions_with_chunks'],
        "Total chunks created": chunk_stats['total_chunks'],
        "Average chunks per session": f"{avg_chunks:.1f}",
        "Chunk size": CHUNK_SIZE,
        "Output file": str(SUSPICIOUS_CHUNKS_FILE)
    }
    
    print_stats("✅ CHUNKING COMPLETE", stats)
    
    return all_chunks


if __name__ == '__main__':
    main()
