from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from models.song import Song

class SongSearchRequest(BaseModel):
    """Request schema for song search"""
    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Bohemian Rhapsody Queen",
                "limit": 10
            }
        }

class SongInfo(BaseModel):
    """Basic song information for search results"""
    id: Optional[int] = Field(None, description="Genius song ID")
    title: str = Field(..., description="Song title")
    artist: str = Field(..., description="Artist name")
    url: Optional[str] = Field(None, description="Genius URL")
    thumbnail: Optional[str] = Field(None, description="Thumbnail image URL")

class SongSearchResponse(BaseModel):
    """Response schema for song search"""
    songs: List[SongInfo] = Field(..., description="List of found songs")
    total_found: int = Field(..., description="Total number of songs found")
    query: str = Field(..., description="Original search query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "songs": [
                    {
                        "id": 12345,
                        "title": "Bohemian Rhapsody",
                        "artist": "Queen",
                        "url": "https://genius.com/Queen-bohemian-rhapsody-lyrics",
                        "thumbnail": "https://images.genius.com/..."
                    }
                ],
                "total_found": 1,
                "query": "Bohemian Rhapsody Queen"
            }
        }

class SongDetailsResponse(BaseModel):
    """Response schema for detailed song information"""
    song: Song = Field(..., description="Complete song details including lyrics and annotations")
    message: str = Field(..., description="Response message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "song": {
                    "id": 12345,
                    "title": "Bohemian Rhapsody",
                    "artist": "Queen",
                    "album": "A Night at the Opera",
                    "genre": "Rock, Progressive Rock",
                    "release_year": 1975
                },
                "message": "Song details retrieved successfully"
            }
        }
