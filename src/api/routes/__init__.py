"""
API routes package.
Contains all FastAPI router definitions.
"""

from .story_routes import router as story_router
from .song_routes import router as song_router

__all__ = ["story_router", "song_router"]