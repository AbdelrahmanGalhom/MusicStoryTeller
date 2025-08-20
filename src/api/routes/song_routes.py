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
    """Dependency to provide Genius service"""
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
    Search for songs on Genius.
    
    Returns a list of matching songs with basic information.
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
    Get detailed information about a specific song.
    
    Includes lyrics, annotations, and metadata.
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
