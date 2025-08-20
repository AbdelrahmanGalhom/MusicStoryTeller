from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .song import Song

class Story(BaseModel):
    """
    Data model for AI-generated stories based on song content.
    
    Represents the output of the story generation process, combining the source
    song information with the AI-generated narrative content. Maintains the
    relationship between source material and generated output.
    
    Attributes:
        song: Complete Song object containing all source metadata and lyrics
        generated_story: AI-generated narrative text inspired by the song
        created_at: Timestamp when the story was generated
        
    Usage:
        Primary response model for story generation API endpoints. Contains
        both the input song data and output story for complete context.
        
    Validation:
        - Song object must be valid according to Song model constraints
        - Generated story is required and must contain actual content
        - Creation timestamp is automatically set during object creation
    """
    song: Song = Field(None, description="Song details including title, artist, album, etc.")
    generated_story: str = Field(..., description="Generated story based on the song")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    