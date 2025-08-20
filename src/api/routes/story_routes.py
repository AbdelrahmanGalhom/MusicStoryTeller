from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import logging

from api.schemas.story_schemas import (
    StoryGenerationRequest,
    StoryResponse,
    HealthResponse
)
from services.langchain_service import LangChainService
from services.genius_service import GeniusClient

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get services
def get_langchain_service() -> LangChainService:
    """Dependency to provide LangChain service"""
    try:
        return LangChainService()
    except Exception as e:
        logger.error(f"Failed to initialize LangChain service: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize story generation service"
        )

@router.post("/generate", response_model=StoryResponse)
async def generate_story(
    request: StoryGenerationRequest,
    langchain_service: LangChainService = Depends(get_langchain_service)
):
    """
    Generate a story from a song name and optional artist.
    
    This endpoint searches for the song, retrieves its data including lyrics
    and annotations, then generates an original story based on the song's themes.
    """
    try:
        logger.info(f"Generating story for song: '{request.song_name}'" + 
                   (f" by {request.artist_name}" if request.artist_name else ""))
        
        story = langchain_service.generate_story_from_song_name(
            song_name=request.song_name,
            artist_name=request.artist_name
        )
        
        return StoryResponse(
            story=story,
            message="Story generated successfully"
        )
        
    except ValueError as e:
        logger.warning(f"Song not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate story: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate story: {str(e)}"
        )

@router.get("/health", response_model=HealthResponse)
async def service_health():
    """Check the health of the story generation services"""
    try:
        # Test services initialization
        langchain_service = LangChainService()
        
        return HealthResponse(
            status="healthy",
            services={
                "langchain": "operational"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="degraded",
            services={
                "langchain": "error" if "langchain" in str(e).lower() else "unknown"
            },
            error=str(e)
        )
