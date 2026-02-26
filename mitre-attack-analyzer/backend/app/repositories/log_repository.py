"""
Repository layer for database operations.
Handles all MongoDB interactions for log analyses.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from beanie import PydanticObjectId
from loguru import logger
from app.models.log_model import LogAnalysis, LogStatus

class LogRepository:
    """Repository for log analysis data access."""
    
    async def create(self, log_analysis: LogAnalysis) -> LogAnalysis:
        """
        Create a new log analysis record.
        
        Args:
            log_analysis: LogAnalysis document to create
            
        Returns:
            Created LogAnalysis document with ID
        """
        await log_analysis.insert()
        return log_analysis
    
    async def find_by_id(self, analysis_id: str) -> Optional[LogAnalysis]:
        """
        Find a log analysis by ID.
        
        Args:
            analysis_id: Document ID
            
        Returns:
            LogAnalysis document if found, None otherwise
        """
        try:
            return await LogAnalysis.get(PydanticObjectId(analysis_id))
        except Exception:
            return None
    
    async def find_by_session(self, session_id: str, limit: int = 100) -> List[LogAnalysis]:
        """
        Find all log analyses for a session.
        
        Args:
            session_id: Session ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of LogAnalysis documents
        """
        return await LogAnalysis.find(
            LogAnalysis.session_id == session_id
        ).sort(-LogAnalysis.analyzed_at).limit(limit).to_list()
    
    async def find_by_status(self, status: LogStatus, limit: int = 100) -> List[LogAnalysis]:
        """
        Find log analyses by status.
        
        Args:
            status: Status to filter by
            limit: Maximum number of results
            
        Returns:
            List of LogAnalysis documents
        """
        return await LogAnalysis.find(
            LogAnalysis.status == status
        ).sort(-LogAnalysis.analyzed_at).limit(limit).to_list()
    
    async def find_recent(self, limit: int = 50) -> List[LogAnalysis]:
        """
        Find recent log analyses.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of LogAnalysis documents sorted by most recent
        """
        return await LogAnalysis.find_all().sort(-LogAnalysis.analyzed_at).limit(limit).to_list()
    
    async def count_by_status(self) -> dict:
        """
        Count analyses by status.
        
        Returns:
            Dictionary with status counts
        """
        try:

            counts = {}
            for status in LogStatus:
                count = await LogAnalysis.find(LogAnalysis.status == status).count()
                counts[status.value] = count
            return counts
        except Exception as e:

            logger.error(f"Error in count_by_status: {str(e)}")
            return {}
    
    async def delete_by_id(self, analysis_id: str) -> bool:
        """
        Delete a log analysis by ID.
        
        Args:
            analysis_id: Document ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            analysis = await self.find_by_id(analysis_id)
            if analysis:
                await analysis.delete()
                return True
            return False
        except Exception:
            return False
    
    async def delete_old_records(self, days: int = 30) -> int:
        """
        Delete records older than specified days.
        
        Args:
            days: Delete records older than this many days
            
        Returns:
            Number of deleted records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await LogAnalysis.find(
            LogAnalysis.analyzed_at < cutoff_date
        ).delete()
        return result.deleted_count if result else 0



log_repository = LogRepository()
