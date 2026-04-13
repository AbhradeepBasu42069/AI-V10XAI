# ============================================================================
# CAMPUSHIRE RECRUITER-CANDIDATE MATCHING SYSTEM
# Main FastAPI Application Entry Point
# ============================================================================
import os
import uvicorn
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import routers
from routers import recruiter, candidate, matching
from routers import profileparser, vector, vector_storage, candidate_matching
from database import initialize_database
from config import APP_NAME, APP_VERSION, print_config_summary

# Load environment variables
load_dotenv()

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================
app = FastAPI(
    title=APP_NAME,
    description="AI-powered recruiter-to-candidate matching system with semantic search",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================================
# CORS CONFIGURATION
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# STARTUP EVENT
# ============================================================================
@app.on_event("startup")
async def startup_event():
    """Initialize database schema and print configuration on startup"""
    try:
        logger.info("="*70)
        logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
        logger.info("="*70)
        
        # Print configuration summary
        print_config_summary()
        
        # Initialize database
        logger.info("Initializing database schema...")
        initialize_database()
        logger.info("✓ Database initialized successfully")
        
        logger.info("✓ Application startup complete")
        
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        # Don't raise - allow app to continue if schema already exists
        pass

# ============================================================================
# ROOT ENDPOINTS
# ============================================================================
@app.get("/")
def home():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {APP_NAME}",
        "version": APP_VERSION,
        "description": "AI-powered recruiter-to-candidate matching system",
        "documentation": "/docs",
        "health_status": "/health"
    }

@app.get("/health")
def health_check():
    """System-wide health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": APP_NAME,
        "version": APP_VERSION
    }

@app.get("/version")
def version_info():
    """Get application version"""
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# INCLUDE ROUTERS (NEW ARCHITECTURE)
# ============================================================================
logger.info("Registering API routers...")

# Main routers for new architecture
app.include_router(recruiter.router, prefix="/api/v1")
app.include_router(candidate.router, prefix="/api/v1")
app.include_router(matching.router, prefix="/api/v1")

# Legacy routers for backward compatibility
app.include_router(profileparser.router)
app.include_router(vector.router)
app.include_router(vector_storage.router)
app.include_router(candidate_matching.router)

logger.info("✓ All routers registered successfully")

# ============================================================================
# ERROR HANDLERS
# ============================================================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return {
        "status": "error",
        "status_code": exc.status_code,
        "detail": exc.detail,
        "timestamp": datetime.now().isoformat()
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "status": "error",
        "status_code": 500,
        "detail": "Internal server error",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# APPLICATION STARTUP
# ============================================================================
if __name__ == "__main__":
    # Get port from environment or default to 8080
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")  # Use 0.0.0.0 for cloud deployment
    
    logger.info(f"Starting server on {host}:{port}")
    
    # Run the application
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )