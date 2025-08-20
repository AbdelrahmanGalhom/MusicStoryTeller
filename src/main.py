from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager

from api.routes import story_routes, song_routes
from helpers.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown operations.
    
    Manages the complete lifecycle of the FastAPI application including
    initialization of services, resource allocation, and graceful shutdown.
    Provides centralized logging for application state changes.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None: Control during application runtime
        
    Process:
        - Startup: Logs application start with version information
        - Runtime: Yields control to FastAPI for request handling
        - Shutdown: Logs graceful application termination
        
    Note:
        This context manager ensures proper resource management and
        provides clear visibility into application lifecycle events.
    """
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    logger.info("Shutting down application")

app = FastAPI(
    title="Music Storyteller API",
    description="Transform songs into engaging stories using AI",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.include_router(story_routes.router, prefix="/api/v1/stories", tags=["stories"])
app.include_router(song_routes.router, prefix="/api/v1/songs", tags=["songs"])

@app.get("/")
async def root():
    """
    Root endpoint providing API information and navigation.
    
    Returns basic information about the Music Storyteller API including
    version, welcome message, and links to documentation. Serves as the
    entry point for API discovery and health verification.
    
    Returns:
        Dictionary containing:
            - message: Welcome message for the API
            - version: Current application version
            - docs: Path to interactive API documentation
            
    Note:
        This endpoint is typically used for API discovery, health checks
        by external services, and providing users with basic information
        about available functionality.
    """
    return {
        "message": "Welcome to Music Storyteller API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """
    Global application health check endpoint.
    
    Provides a simple health status indicator for the overall application.
    Used by load balancers, monitoring systems, and deployment tools to
    verify basic application availability and routing readiness.
    
    Returns:
        Dictionary containing:
            - status: Overall health status ("healthy")
            - service: Service identifier for monitoring
            
    Note:
        This is a lightweight health check. For detailed service status
        including AI components, use /api/v1/stories/health endpoint.
        
    Response Format:
        Always returns 200 status if application is running, with
        simple JSON indicating service availability.
    """
    return {"status": "healthy", "service": "music-storyteller"}

