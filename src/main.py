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
    """Application lifespan manager"""
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
    """Root endpoint with basic info"""
    return {
        "message": "Welcome to Music Storyteller API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "music-storyteller"}

