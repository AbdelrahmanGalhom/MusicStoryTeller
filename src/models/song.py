from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Song(BaseModel):
    """
    Comprehensive data model for song information and metadata.
    
    Represents a complete song entity with all available data from Genius API
    including metadata, lyrics, and community annotations. Uses Pydantic for
    data validation and serialization.
    
    Attributes:
        id: Unique identifier from Genius database
        title: Official song title (required)
        artist: Primary artist or band name (required)
        album: Album or release name (optional)
        genre: Musical genre classification (optional)
        release_year: Year of release with validation bounds
        lyrics: Complete song lyrics text (optional)
        lyrics_url: Direct link to Genius lyrics page
        created_at: Timestamp when object was created
        annotations: List of expert explanations and interpretations
        
    Validation:
        - Title and artist are required with minimum length
        - Release year must be between 1900-2030 if provided
        - All timestamps are automatically generated
        - Annotations default to empty list if not provided
    """
    id: Optional[int] = Field(None, description="Genius song ID")
    title: str = Field(..., min_length=1, description="Song title")
    artist: str = Field(..., min_length=1, description="Artist name")
    album: Optional[str] = Field(None, description="Album name")
    genre: Optional[str] = Field(None, description="Musical genre")
    release_year: Optional[int] = Field(None, ge=1900, le=2030, description="Release year")
    lyrics: Optional[str] = Field(None, description="Song lyrics")
    lyrics_url: Optional[str] = Field(None, description="URL to lyrics on Genius")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    annotations: List[str] = Field(default_factory=list, description="List of annotations for the song")
