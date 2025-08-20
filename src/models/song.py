from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Song(BaseModel):
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
