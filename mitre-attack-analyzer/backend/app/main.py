"""
FastAPI Main Application.
Entry point for the MITRE ATT&CK Log Analyzer backend.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
import sys

from app.config import settings
from app.models.log_model import LogAnalysis
from app.controllers.log_controller import router as log_router
from app.services.ml_service import ml_service


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting MITRE ATT&CK Log Analyzer API")
    
    try:
        # Initialize MongoDB
        logger.info(f"Connecting to MongoDB: {settings.MONGODB_URL}")
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        await init_beanie(
            database=client[settings.MONGODB_DB_NAME],
            document_models=[LogAnalysis]
        )
        logger.success("✅ MongoDB connected successfully")
        
        # Load ML model
        logger.info("Loading ML model...")
        await ml_service.load_model()
        logger.success("✅ ML model loaded successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise
    
    logger.success("🎉 Application started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    logger.success("✅ Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="MITRE ATT&CK Log Analyzer API",
    description="Backend API for analyzing security logs and detecting MITRE ATT&CK techniques",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler to ensure CORS headers on errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions and ensure CORS headers are included."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
        }
    )


# Include routers
app.include_router(log_router)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "MITRE ATT&CK Log Analyzer API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "model_loaded": ml_service.is_loaded()
    }


# Health check endpoint
@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": ml_service.is_loaded()
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info"
    )
