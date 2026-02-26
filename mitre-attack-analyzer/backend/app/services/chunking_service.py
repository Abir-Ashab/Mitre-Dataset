"""
Chunking Service - Split full session logs into analyzable chunks
Based on the data preparation pipeline logic
"""

import json
from typing import List, Dict, Any
from datetime import datetime
from loguru import logger


class ChunkingService:
    """Service to chunk full session logs into smaller pieces"""
    
    CHUNK_SIZE = 7
    MIN_CHUNK_SIZE = 5
    
    def __init__(self):
        """Initialize chunking service"""
        pass
    
    def parse_session_log(self, log_content: str) -> List[Dict[str, Any]]:
        """
        Parse session log JSON content
        
        Args:
            log_content: JSON string containing array of logs
            
        Returns:
            List of log objects
        """
        try:
            logs = json.loads(log_content)
            

            if isinstance(logs, dict):
                logs = [logs]
            

            if not isinstance(logs, list):
                raise ValueError("Log content must be a JSON array or object")
            
            return logs
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
    
    def get_timestamp(self, log: Dict[str, Any]) -> str:
        """
        Extract timestamp from log for sorting
        
        Args:
            log: Log object
            
        Returns:
            Timestamp string
        """
        timestamp_fields = [
            '@timestamp',
            'timestamp',
            'event.created',
            'winlog.time_created',
            'event_time',
            'created_at'
        ]
        
        for field in timestamp_fields:

            if field in log:
                return str(log[field])
            

            if '.' in field:
                parts = field.split('.')
                obj = log
                try:
                    for part in parts:
                        obj = obj[part]
                    return str(obj)
                except (KeyError, TypeError):
                    continue
        

        return ""
    
    def create_chunks(self, logs: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Create fixed-size chunks from logs
        
        Args:
            logs: List of log objects
            
        Returns:
            List of chunks (each chunk is a list of logs)
        """

        sorted_logs = sorted(logs, key=self.get_timestamp)
        
        chunks = []
        for i in range(0, len(sorted_logs), self.CHUNK_SIZE):
            chunk = sorted_logs[i:i + self.CHUNK_SIZE]
            

            if len(chunk) >= self.MIN_CHUNK_SIZE or i + self.CHUNK_SIZE >= len(sorted_logs):
                chunks.append(chunk)
        
        return chunks
    
    def create_chunk_metadata(
        self, 
        chunk: List[Dict[str, Any]], 
        chunk_index: int, 
        session_id: str,
        total_chunks: int
    ) -> Dict[str, Any]:
        """
        Create metadata for a chunk
        
        Args:
            chunk: List of logs in the chunk
            chunk_index: Index of this chunk in the session
            session_id: Session identifier
            total_chunks: Total number of chunks in session
            
        Returns:
            Metadata dictionary
        """
        timestamps = [self.get_timestamp(log) for log in chunk]
        valid_timestamps = [t for t in timestamps if t]
        
        metadata = {
            "session_id": session_id,
            "chunk_index": chunk_index,
            "total_chunks": total_chunks,
            "chunk_size": len(chunk),
            "start_time": min(valid_timestamps) if valid_timestamps else "unknown",
            "end_time": max(valid_timestamps) if valid_timestamps else "unknown",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return metadata
    
    def chunk_session_logs(
        self, 
        log_content: str, 
        session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Parse and chunk session logs
        
        Args:
            log_content: JSON string containing logs
            session_id: Session identifier
            
        Returns:
            List of chunk objects with metadata and logs
        """
        try:

            logs = self.parse_session_log(log_content)
            logger.info(f"Parsed {len(logs)} logs from session {session_id}")
            

            chunks = self.create_chunks(logs)
            logger.info(f"Created {len(chunks)} chunks from session {session_id}")
            

            chunk_objects = []
            for idx, chunk in enumerate(chunks):
                metadata = self.create_chunk_metadata(chunk, idx, session_id, len(chunks))
                
                chunk_obj = {
                    "metadata": metadata,
                    "logs": chunk,
                    "logs_json": json.dumps(chunk, ensure_ascii=False)
                }
                
                chunk_objects.append(chunk_obj)
            
            return chunk_objects
            
        except Exception as e:
            logger.error(f"Error chunking session logs: {str(e)}")
            raise



chunking_service = ChunkingService()
