"""
Repository for Session Chunk operations
Handles database interactions for session chunks
"""

from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId
from loguru import logger

from app.models.session_chunk_model import SessionChunk


class SessionChunkRepository:
    """Repository for session chunk data access"""
    
    async def create_chunk(self, chunk_data: SessionChunk) -> SessionChunk:
        """
        Create a new session chunk record
        
        Args:
            chunk_data: SessionChunk document to create
            
        Returns:
            Created SessionChunk document with ID
        """
        await chunk_data.insert()
        return chunk_data
    
    async def create_many_chunks(self, chunks: List[SessionChunk]) -> List[SessionChunk]:
        """
        Create multiple session chunks at once
        
        Args:
            chunks: List of SessionChunk documents
            
        Returns:
            List of created chunks with IDs
        """
        await SessionChunk.insert_many(chunks)
        return chunks
    
    async def find_by_session(self, session_id: str, skip: int = 0, limit: int = 50) -> tuple[List[SessionChunk], int]:
        """
        Find chunks for a session with pagination
        
        Args:
            session_id: Session identifier
            skip: Number of chunks to skip
            limit: Maximum chunks to return
            
        Returns:
            Tuple of (chunks list, total count)
        """
        total = await SessionChunk.find(
            SessionChunk.session_id == session_id
        ).count()
        
        chunks = await SessionChunk.find(
            SessionChunk.session_id == session_id
        ).sort(+SessionChunk.chunk_index).skip(skip).limit(limit).to_list()
        
        return chunks, total
    
    async def find_chunk_by_id(self, chunk_id: str) -> Optional[SessionChunk]:
        """
        Find a chunk by its ID
        
        Args:
            chunk_id: Chunk document ID
            
        Returns:
            SessionChunk if found, None otherwise
        """
        try:
            return await SessionChunk.get(PydanticObjectId(chunk_id))
        except Exception:
            return None
    
    async def get_all_sessions(self, skip: int = 0, limit: int = 20) -> tuple[List[dict], int]:
        """
        Get list of all unique sessions with metadata (paginated)
        
        Args:
            skip: Number of sessions to skip
            limit: Maximum sessions to return
            
        Returns:
            Tuple of (session list, total count)
        """
        try:
            # Get all chunks and group by session in Python (simpler than aggregation)
            all_chunks = await SessionChunk.find_all().sort(-SessionChunk.created_at).to_list()
            
            # Group by session_id
            sessions_dict = {}
            for chunk in all_chunks:
                sid = chunk.session_id
                if sid not in sessions_dict:
                    sessions_dict[sid] = {
                        "session_id": sid,
                        "session_name": chunk.session_name,
                        "total_chunks": chunk.total_chunks,
                        "analyzed_chunks": 0,
                        "created_at": chunk.created_at.isoformat() if chunk.created_at else None
                    }
                if chunk.is_analyzed:
                    sessions_dict[sid]["analyzed_chunks"] += 1
            
            # Convert to list and sort by created_at
            sessions = list(sessions_dict.values())
            sessions.sort(key=lambda x: x["created_at"] or "", reverse=True)
            
            total = len(sessions)
            return sessions[skip:skip+limit], total
        except Exception as e:
            logger.error(f"Error getting sessions: {str(e)}")
            return [], 0
    
    async def update_chunk_analysis(
        self, 
        chunk_id: str, 
        analysis_id: str
    ) -> bool:
        """
        Mark chunk as analyzed and link to analysis
        
        Args:
            chunk_id: Chunk document ID
            analysis_id: LogAnalysis document ID
            
        Returns:
            True if updated, False otherwise
        """
        try:
            chunk = await self.find_chunk_by_id(chunk_id)
            if chunk:
                chunk.is_analyzed = True
                chunk.analysis_id = analysis_id
                chunk.analyzed_at = datetime.utcnow()
                await chunk.save()
                return True
            return False
        except Exception:
            return False
    
    async def delete_session(self, session_id: str) -> int:
        """
        Delete all chunks for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Number of chunks deleted
        """
        result = await SessionChunk.find(
            SessionChunk.session_id == session_id
        ).delete()
        return result.deleted_count if result else 0


# Global repository instance
session_chunk_repository = SessionChunkRepository()
