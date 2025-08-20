import os
import logging
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

from models.song import Song
from models.story import Story
from helpers.config import get_settings
from services.genius_service import GeniusClient


logger = logging.getLogger(__name__)


class LangChainService:
    """Service class for generating stories from songs using LangChain with Google Gemini."""
    
    def __init__(self):
        """Initialize the LangChain service with Gemini using config settings."""
        logger.info("Initializing LangChain service")
        
        self.settings = get_settings()
        
        if not self.settings.GEMINI_API_KEY:
            logger.error("Gemini API key is missing from configuration")
            raise ValueError("Gemini API key is required in configuration.")
        
        logger.debug(f"Using Gemini model: {self.settings.GEMINI_MODEL}")
        logger.debug(f"Temperature: {self.settings.GEMINI_TEMPERATURE}, Max tokens: {self.settings.GEMINI_MAX_TOKENS}")
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                google_api_key=self.settings.GEMINI_API_KEY,
                model=self.settings.GEMINI_MODEL,
                temperature=self.settings.GEMINI_TEMPERATURE,
                max_tokens=self.settings.GEMINI_MAX_TOKENS
            )
            logger.info("Successfully initialized ChatGoogleGenerativeAI")
        except Exception as e:
            logger.error(f"Failed to initialize ChatGoogleGenerativeAI: {str(e)}")
            raise
        
        # Initialize Genius service for song data retrieval
        try:
            self.genius_service = GeniusClient()
            logger.info("Successfully initialized Genius service")
        except Exception as e:
            logger.error(f"Failed to initialize Genius service: {str(e)}")
            raise
        
        # Initialize the story generation chain
        self._setup_story_generation_chain()
        logger.info("LangChain service initialization completed")
    
    def _setup_story_generation_chain(self):
        """Set up the LangChain chain for story generation."""
        logger.debug("Setting up story generation chain")
        
        story_prompt_template = """
        You are a creative storyteller who transforms songs into engaging narratives.
        
        Based on the following song information, create an original story that captures the essence and themes of the song:
        
        Song Title: {title}
        Artist: {artist}
        Album: {album}
        Genre: {genre}
        Release Year: {release_year}
        
        Song Annotations (Expert Analysis): {annotations}
        
        Lyrical Themes and Context Analysis: {lyrics_summary}
        
        Instructions:
        - Create an original narrative story inspired by the song's themes and emotions
        - Use the annotations to understand deeper meanings and cultural context
        - Incorporate the emotional essence from the lyrics
        - Quote the lyrics only if they are essential to the story
        - Do not reproduce lyrics verbatim, focus on thematic elements
        - Make the story engaging, vivid, and emotionally resonant
        - Length should be 300-500 words
        - Focus on character development and atmospheric storytelling
        
        Story:
        """
        
        self.story_prompt = PromptTemplate(
            input_variables=["title", "artist", "album", "genre", "release_year", "annotations", "lyrics_summary"],
            template=story_prompt_template
        )
        
        self.story_chain = self.story_prompt | self.llm
        
        logger.debug("Story generation chain setup completed")
    
    def analyze_lyrics(self, lyrics: Optional[str]) -> str:
        """
        Analyze song lyrics to provide a combined thematic and contextual summary in one output,
        without reproducing copyrighted content.

        Args:
            lyrics: The song lyrics

        Returns:
            A single string summarizing:
                - Main emotional themes
                - Story elements or narrative present

        """
        logger.debug("Starting lyrics thematic and contextual analysis")

        if not lyrics or len(lyrics.strip()) == 0:
            logger.warning("No lyrics provided for combined analysis")
            return "No lyrical content available for analysis."

        summary_prompt_template = """
        Analyze the following song lyrics and provide a summary covering:

        - Main emotional themes
        - Story elements or narrative present
        - Overall mood and atmosphere
        - Key symbolic or metaphorical elements
        - Emotional journey or progression
        - Characters or personas mentioned
        - Setting or atmosphere described
        - Key metaphors or imagery
        - Narrative arc or story elements

        Do NOT reproduce or directly quote the lyrics. Provide only a thematic and contextual analysis.

        Lyrics: {lyrics}

        Combined Thematic and Contextual Summary:
        """

        summary_prompt = PromptTemplate(
            input_variables=["lyrics"],
            template=summary_prompt_template
        )

        summary_chain = summary_prompt | self.llm

        try:
            truncated_lyrics = lyrics[:1500]  
            logger.debug(f"Processing truncated lyrics for summary analysis: {len(truncated_lyrics)} characters")

            response = summary_chain.invoke({"lyrics": truncated_lyrics})
            summary = response.content.strip() if hasattr(response, 'content') else str(response).strip()

            logger.info(f"Successfully generated lyrics summary: {len(summary)} characters")
            logger.debug(f"Summary preview: {summary[:100]}...")

            return summary

        except Exception as e:
            logger.error(f"Failed to analyze lyrics summary: {str(e)}")
            return f"Unable to analyze lyrics: {str(e)}"



    def generate_story_from_song_name(self, song_name: str, artist_name: Optional[str] = None) -> Story:
        """
        Complete chain: Search song -> Retrieve data -> Generate story.
        
        Args:
            song_name: Name of the song to search for
            artist_name: Optional artist name to improve search accuracy
            
        Returns:
            Story object with generated content
        """
        logger.info(f"Starting story generation for song: '{song_name}'" + 
                   (f" by {artist_name}" if artist_name else ""))
        
        try:
            # Step 1: Search for song using Genius service
            search_query = f"{song_name} {artist_name}" if artist_name else song_name
            logger.debug(f"Searching Genius with query: '{search_query}'")
            
            search_results = self.genius_service.search_song(search_query)
            
            if not search_results:
                logger.warning(f"No search results found for song: '{song_name}'")
                raise ValueError(f"Song '{song_name}' not found on Genius.")
            
            logger.info(f"Found {len(search_results)} search results for '{song_name}'")
            
            # Get the first result's ID
            song_id = search_results[0].get('id')
            if not song_id:
                logger.error(f"Could not extract song ID from search results for '{song_name}'")
                raise ValueError(f"Could not extract song ID for '{song_name}'.")
            
            logger.debug(f"Using song ID: {song_id}")
            
            # Step 2: Retrieve full song data with lyrics and annotations
            logger.debug(f"Retrieving complete song data for ID: {song_id}")
            song = self.genius_service.get_song_lyrics_with_annotations(song_id)
            
            if not song:
                logger.error(f"Failed to retrieve complete song data for ID: {song_id}")
                raise ValueError(f"Could not retrieve complete data for song ID: {song_id}")
            
            logger.info(f"Successfully retrieved song data: '{song.title}' by {song.artist}")
            
            # Step 3: Generate story using the complete song data
            logger.debug("Starting story generation from song data")
            story_content = self.generate_story_from_song(song)
            
            # Step 4: Create and return Story object
            story = Story(
                song=song,
                generated_story=story_content
            )
            
            logger.info(f"Successfully generated story for '{song_name}' - Story length: {len(story_content)} characters")
            return story
            
        except Exception as e:
            logger.error(f"Failed to generate story for '{song_name}': {str(e)}")
            raise Exception(f"Failed to generate story: {str(e)}")


    def generate_story_from_song(self, song: Song) -> str:
        """
        Generate a story from a Song object using lyrics, annotations, and thematic analysis.
        
        Args:
            song: Song object with all necessary data
            
        Returns:
            Generated story as string
        """
        logger.info(f"Generating story from song object: '{song.title}' by {song.artist}")
        
        try:
            # Generate analysis of lyrics
            logger.debug("Generating analysis of lyrics")
            lyrics_summary = self.analyze_lyrics(song.lyrics)
            
            # Prepare annotations summary
            annotations_count = len(song.annotations) if song.annotations else 0
            logger.debug(f"Processing {annotations_count} annotations")
            annotations_text = "\n".join([f"- {ann}" for ann in song.annotations]) if song.annotations else "No expert annotations available"
            
            # Log input data summary
            logger.debug(f"Story generation inputs - Title: '{song.title}', Artist: '{song.artist}', "
                        f"Album: '{song.album or 'Unknown'}', Genre: '{song.genre or 'Unknown'}', "
                        f"Year: '{song.release_year or 'Unknown'}', Annotations: {annotations_count}")
            
            # Run the story generation chain with all available data
            logger.debug("Running story generation chain")
            response = self.story_chain.invoke({
                "title": song.title,
                "artist": song.artist,
                "album": song.album or "Unknown Album",
                "genre": song.genre or "Unknown Genre",
                "release_year": song.release_year or "Unknown Year",
                "annotations": annotations_text,
                "lyrics_summary": lyrics_summary,
            })
            
            # Extract content from response
            story = response.content.strip() if hasattr(response, 'content') else str(response).strip()
            logger.info(f"Successfully generated story for '{song.title}' - Length: {len(story)} characters")
            logger.debug(f"Story preview: {story[:150]}...")
            
            return story
            
        except Exception as e:
            logger.error(f"Failed to generate story from song '{song.title}': {str(e)}")
            raise Exception(f"Failed to generate story from song data: {str(e)}")
