from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import logging

from api.schemas.song_schemas import (
    SongSearchRequest,
    SongSearchResponse,
    SongDetailsResponse
)
from services.genius_service import GeniusClient

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get services
def get_genius_service() -> GeniusClient:
    """
    Dependency injection for Genius API service.
    
    Provides a configured Genius client instance for song search and
    data retrieval endpoints. Handles initialization errors gracefully
    by converting them to appropriate HTTP exceptions.
    
    Returns:
        Configured GeniusClient instance ready for API operations
        
    Raises:
        HTTPException: 500 status if service initialization fails
        
    Note:
        This dependency ensures proper error handling and service
        availability for all song-related endpoints.
    """
    try:
        return GeniusClient()
    except Exception as e:
        logger.error(f"Failed to initialize Genius service: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize music data service"
        )

@router.post("/search", response_model=SongSearchResponse)
async def search_songs(
    request: SongSearchRequest,
    genius_service: GeniusClient = Depends(get_genius_service)
):
    """
    Search for songs using text query across Genius database.
    
    Performs fuzzy text search to find songs matching the provided query.
    Returns basic song information for each match, ordered by relevance.
    Supports searching by song title, artist name, or combination.
    
    Args:
        request: Search request containing query string and optional result limit
        genius_service: Injected Genius API client for search operations
        
    Returns:
        SongSearchResponse containing:
            - List of matching songs with basic metadata
            - Total number of results found
            - Original search query for reference
            
    Raises:
        HTTPException:
            - 404 if no songs found matching the query
            - 500 if search operation fails due to service issues
            
    Note:
        Results are limited by configuration to prevent excessive API usage.
        Search is case-insensitive and supports partial matching.
    """
    try:
        logger.info(f"Searching for songs: '{request.query}'")
        
        search_results = genius_service.search_song(
            query=request.query,
            limit=request.limit
        )
        
        if not search_results:
            raise HTTPException(
                status_code=404,
                detail=f"No songs found for query: '{request.query}'"
            )
        
        # Transform results to response format
        songs = []
        for result in search_results:
            songs.append({
                "id": result.get("id"),
                "title": result.get("title", ""),
                "artist": result.get("primary_artist", {}).get("name", ""),
                "url": result.get("url", ""),
                "thumbnail": result.get("header_image_thumbnail_url", "")
            })
        
        return SongSearchResponse(
            songs=songs,
            total_found=len(songs),
            query=request.query
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search songs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search songs: {str(e)}"
        )

@router.get("/{song_id}", response_model=SongDetailsResponse)
async def get_song_details(
    song_id: int,
    genius_service: GeniusClient = Depends(get_genius_service)
):
    """
    Retrieve comprehensive information for a specific song by ID.
    
    Fetches complete song data including metadata, lyrics, and community
    annotations from Genius. This endpoint provides all available information
    for a song, including expert interpretations and cultural context.
    
    Args:
        song_id: Unique Genius song identifier
        genius_service: Injected Genius API client for data retrieval
        
    Returns:
        SongDetailsResponse containing:
            - Complete song object with all metadata
            - Full lyrics text (if available)
            - Community annotations and explanations
            - Album, genre, and release information
            
    Raises:
        HTTPException:
            - 404 if song ID is not found in Genius database
            - 500 if data retrieval fails due to service issues
            
    Process:
        1. Fetches structured song metadata from API
        2. Scrapes lyrics from Genius web page
        3. Retrieves all community annotations
        4. Combines data into comprehensive Song object
        
    Note:
        This endpoint is typically used after song search to get
        complete information for story generation or detailed analysis.
    """
    try:
        logger.info(f"Getting details for song ID: {song_id}")
        
        song = genius_service.get_song_lyrics_with_annotations(song_id)
        
        if not song:
            raise HTTPException(
                status_code=404,
                detail=f"Song with ID {song_id} not found"
            )
        
        return SongDetailsResponse(
            song=song,
            message="Song details retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get song details: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get song details: {str(e)}"
        )
