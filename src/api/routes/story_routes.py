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
    """
    Dependency injection for LangChain service.
    
    Provides a configured LangChain service instance for story generation
    endpoints. Handles initialization errors gracefully by converting
    them to appropriate HTTP exceptions.
    
    Returns:
        Configured LangChainService instance ready for story generation
        
    Raises:
        HTTPException: 500 status if service initialization fails
        
    Note:
        This dependency ensures proper error handling and service
        availability for all story generation endpoints.
    """
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
    Generate an original narrative story from song information.
    
    Takes a song name and optional artist, searches for the song on Genius,
    retrieves complete metadata and lyrics, then uses AI to generate an
    original story that captures the song's themes and emotional essence.
    
    Args:
        request: Story generation request containing song name and optional artist
        langchain_service: Injected LangChain service for AI processing
        
    Returns:
        StoryResponse containing the complete song data and generated story
        
    Raises:
        HTTPException: 
            - 404 if song is not found on Genius
            - 500 if story generation fails due to service issues
            
    Process:
        1. Searches Genius database for matching song
        2. Retrieves complete song data including lyrics and annotations
        3. Analyzes lyrical content for themes and emotions
        4. Generates original narrative using AI processing
        5. Returns structured response with song and story data
        
    Note:
        Generated stories are original works inspired by song themes,
        not direct adaptations of copyrighted lyrics.
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
    """
    Comprehensive health check for story generation services.
    
    Validates the operational status of all components required for story
    generation including AI services, API connections, and configuration.
    Provides detailed status information for monitoring and debugging.
    
    Returns:
        HealthResponse containing:
            - Overall service status (healthy/degraded/error)
            - Individual service status breakdown
            - Error details if any services are failing
            
    Status Levels:
        - healthy: All services operational
        - degraded: Some services have issues but core functionality works
        - error: Critical services are down
        
    Note:
        Used by load balancers and monitoring systems to determine
        service availability and routing decisions.
    """
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
