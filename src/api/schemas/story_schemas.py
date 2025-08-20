from pydantic import BaseModel, Field
from typing import Optional, Dict
from models.story import Story

class StoryGenerationRequest(BaseModel):
    """Request schema for story generation"""
    song_name: str = Field(..., min_length=1, max_length=200, description="Name of the song")
    artist_name: Optional[str] = Field(None, max_length=200, description="Artist name (optional for better search)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "song_name": "Bohemian Rhapsody",
                "artist_name": "Queen"
            }
        }

class StoryResponse(BaseModel):
    """Response schema for generated story"""
    story: Story = Field(..., description="Generated story with song details")
    message: str = Field(..., description="Response message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "story": {
                    "song": {
                        "id": 12345,
                        "title": "Bohemian Rhapsody",
                        "artist": "Queen",
                        "album": "A Night at the Opera",
                        "genre": "Rock, Progressive Rock",
                        "release_year": 1975
                    },
                    "generated_story": "In the depths of a young man's troubled mind...",
                    "created_at": "2024-01-15T10:30:00Z"
                },
                "message": "Story generated successfully"
            }
        }

class HealthResponse(BaseModel):
    """Response schema for health check"""
    status: str = Field(..., description="Overall service status")
    services: Dict[str, str] = Field(..., description="Status of individual services")
    error: Optional[str] = Field(None, description="Error message if any")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "services": {
                    "langchain": "operational",
                    "genius": "operational"
                }
            }
        }
