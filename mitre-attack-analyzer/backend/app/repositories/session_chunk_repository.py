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
        if not chunks:
            return []
        
        try:

            logger.info(f"Starting bulk insert of {len(chunks)} chunks...")
            await SessionChunk.insert_many(chunks)
            logger.info(f"Successfully inserted {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error inserting chunks: {str(e)}")
            raise
    
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
        Optimized approach: Only fetch chunk_index=0 for each session (contains all session metadata)
        
        Args:
            skip: Number of sessions to skip
            limit: Maximum sessions to return
            
        Returns:
            Tuple of (session list, total count)
        """
        try:


            first_chunks = await SessionChunk.find(
                SessionChunk.chunk_index == 0
            ).sort(-SessionChunk.created_at).to_list()
            
            logger.info(f"Fetched {len(first_chunks)} session first chunks")
            

            sessions = []
            session_ids = []
            
            for chunk in first_chunks:
                session_ids.append(chunk.session_id)
                sessions.append({
                    "session_id": chunk.session_id,
                    "session_name": chunk.session_name,
                    "total_chunks": chunk.total_chunks,
                    "analyzed_chunks": 0,
                    "created_at": chunk.created_at.isoformat() if chunk.created_at else None
                })
            


            paginated_sessions = sessions[skip:skip+limit]
            for session in paginated_sessions:
                analyzed_count = await SessionChunk.find(
                    SessionChunk.session_id == session["session_id"],
                    SessionChunk.is_analyzed == True
                ).count()
                session["analyzed_chunks"] = analyzed_count
            
            total = len(sessions)
            logger.info(f"Returning {len(paginated_sessions)} sessions out of {total} total")
            return paginated_sessions, total
        except Exception as e:
            logger.error(f"Error getting sessions: {str(e)}")
            return [], 0
    
    async def update_chunk_analysis(
        self, 
        session_id: str,
        chunk_index: int,
        analysis_id: str,
        analysis_status: str,
        analysis_result: dict
    ) -> Optional[SessionChunk]:
        """
        Mark chunk as analyzed and save analysis results
        
        Args:
            session_id: Session identifier
            chunk_index: Chunk index
            analysis_id: LogAnalysis document ID
            analysis_status: Analysis status (Normal/Suspicious/Unknown)
            analysis_result: Full analysis result dictionary
            
        Returns:
            Updated SessionChunk if found, None otherwise
        """
        try:
            chunk = await SessionChunk.find_one(
                SessionChunk.session_id == session_id,
                SessionChunk.chunk_index == chunk_index
            )
            if chunk:
                chunk.is_analyzed = True
                chunk.analysis_id = analysis_id
                chunk.analysis_status = analysis_status
                chunk.analysis_result = analysis_result
                chunk.analyzed_at = datetime.utcnow()
                await chunk.save()
                logger.info(f"Updated chunk {chunk_index} analysis: {analysis_status}")
                return chunk
            logger.warning(f"Chunk not found: session={session_id}, index={chunk_index}")
            return None
        except Exception as e:
            logger.error(f"Error updating chunk analysis: {str(e)}")
            return None
    
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



session_chunk_repository = SessionChunkRepository()
