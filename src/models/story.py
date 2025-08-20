from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .song import Song

class Story(BaseModel):
    song: Song = Field(None, description="Song details including title, artist, album, etc.")
    generated_story: str = Field(..., description="Generated story based on the song")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    