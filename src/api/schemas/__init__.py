"""
API schemas package.
Contains Pydantic models for request/response validation.
"""

from .story_schemas import (
    StoryGenerationRequest,
    StoryResponse,
    HealthResponse
)
from .song_schemas import (
    SongSearchRequest,
    SongSearchResponse,
    SongDetailsResponse,
    SongInfo
)

__all__ = [
    "StoryGenerationRequest",
    "StoryResponse", 
    "HealthResponse",
    "SongSearchRequest",
    "SongSearchResponse",
    "SongDetailsResponse",
    "SongInfo"
]
