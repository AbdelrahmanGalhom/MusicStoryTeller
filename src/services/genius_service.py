import requests
import logging
import time
import re
from typing import Optional, Dict, List, Any
from helpers.config import get_settings
from models.song import Song
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GeniusClient:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.GENIUS_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.settings.GENIUS_API_KEY}",
            "User-Agent": f"{self.settings.APP_NAME}/{self.settings.APP_VERSION}"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """HTTP request wrapper with error handling and rate limiting"""
        try:
            url = f"{self.base_url}{endpoint}"
            time.sleep(self.settings.GENIUS_REQUEST_DELAY)
            logger.info(f"Making request to: {url}")
            
            response = self.session.get(url, params=params, timeout=self.settings.GENIUS_TIMEOUT)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Genius API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Genius API: {e}")
            return None
    
    def _make_web_request(self, url: str) -> Optional[str]:
        """Make web request for scraping with proper headers"""
        try:
            time.sleep(self.settings.GENIUS_REQUEST_DELAY)
            response = requests.get(
                url, 
                timeout=self.settings.GENIUS_TIMEOUT,
                headers={"User-Agent": f"{self.settings.APP_NAME}/{self.settings.APP_VERSION}"}
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Failed to fetch web content from {url}: {e}")
            return None
    
    def _extract_song_metadata(self, song_details: Dict) -> Dict:
        """Extract and parse song metadata from API response"""
        metadata = {
            'album': song_details.get("album", {}).get("name") if song_details.get("album") else None,
            'release_year': None,
            'genre': None
        }
        
        # Extract release year
        release_date = song_details.get("release_date_for_display")
        if release_date:
            year_match = re.search(r'\b(19|20)\d{2}\b', release_date)
            if year_match:
                try:
                    metadata['release_year'] = int(year_match.group())
                except ValueError:
                    logger.warning(f"Could not parse release year from: {release_date}")
        
        # Extract genre from tags
        tags = song_details.get("tags", [])
        if tags:
            genre_tags = [tag.get("name", "") for tag in tags if tag.get("name")]
            if genre_tags:
                metadata['genre'] = ", ".join(genre_tags[:3])
        
        return metadata
    
    def _scrape_lyrics(self, lyrics_url: str) -> Optional[str]:
        """Scrape lyrics from Genius lyrics page"""
        logger.info(f"Scraping lyrics from: {lyrics_url}")
        
        html_content = self._make_web_request(lyrics_url)
        if not html_content:
            return None
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find lyrics containers with more specific selectors
        lyrics_containers = (
            soup.find_all('div', {'data-lyrics-container': 'true'}) or
            soup.find_all('div', class_=re.compile(r'Lyrics__Container')) or
            soup.find_all('div', class_=re.compile(r'lyrics')) or
            soup.find_all('div', id=re.compile(r'lyrics'))
        )
        
        if not lyrics_containers:
            logger.warning(f"Could not find lyrics container on page: {lyrics_url}")
            return None
        
        # Extract and format lyrics
        lyrics_parts = []
        for container in lyrics_containers:
            # Remove unwanted elements
            for unwanted in container.find_all(["script", "style", "noscript"]):
                unwanted.decompose()
            
            # Remove ads, annotations buttons, and other UI elements
            for unwanted in container.find_all(attrs={"class": re.compile(r"InreadAd|RightSidebar|SongHeaderDesktop|SongHeaderMobile|Annotation|ReferentFragmentVariantdesktop")}):
                unwanted.decompose()
            
            # Remove data attributes that might contain annotation markup
            for element in container.find_all(attrs={"data-click-to-annotate": True}):
                # Keep the text content but remove the annotation wrapper
                element.unwrap()
            
            # Remove contributor/translation info and song descriptions
            for unwanted in container.find_all(attrs={"class": re.compile(r"Contributors|Translations|SongDescription|HeaderWithSmallTitle")}):
                unwanted.decompose()
            
            # Remove "Read More" links and song info
            for unwanted in container.find_all(string=re.compile(r"Read More|Contributors|Translations|Lyrics")):
                if unwanted.parent:
                    unwanted.parent.decompose()
            
            # Remove language list and metadata at the top
            for unwanted in container.find_all(text=re.compile(r"Nederlands|Türkçe|Español|srpski|Русский|Português|فارسی|Italiano|Magyar|Deutsch|Français|hrvatski|Ελληνικά|Українська|Polski|Română|Slovenščina|Čechy|Català")):
                if unwanted.parent:
                    unwanted.parent.decompose()
            
            # Handle <br> and <p> tags for proper line breaks
            for br in container.find_all("br"):
                br.replace_with("\n")
            
            for p in container.find_all("p"):
                if p.get_text(strip=True):
                    p.insert_after(soup.new_string("\n"))
            
            # Extract text while preserving structure
            text = container.get_text(separator='\n', strip=True)
            
            # Clean up the extracted text
            if text.strip():
                lyrics_parts.append(text)
        
        if not lyrics_parts:
            logger.warning(f"No lyrics text found on page: {lyrics_url}")
            return None
        
        combined_lyrics = '\n'.join(lyrics_parts)
        lyrics = self._format_lyrics(combined_lyrics)
        logger.info(f"Successfully scraped and formatted lyrics ({len(lyrics)} characters)")
        return lyrics
    
    def search_song(self, query: str, limit: Optional[int] = None) -> List[Dict]:
        """Search for songs on Genius"""
        limit = limit or self.settings.GENIUS_MAX_SEARCH_RESULTS
        logger.info(f"Searching for song: {query}")
            
        response = self._make_request("/search", {"q": query, "per_page": limit})
        if not response:
            logger.warning(f"No response received for search: {query}")
            return []
        
        songs = [hit.get("result", {}) for hit in response.get("response", {}).get("hits", [])]
        logger.info(f"Found {len(songs)} songs for query: {query}")
        return songs
    
    def get_song_details(self, song_id: int) -> Optional[Dict]:
        """Get detailed song information"""
        logger.info(f"Getting details for song ID: {song_id}")
        
        response = self._make_request(f"/songs/{song_id}", {"text_format": "plain"})
        if not response:
            logger.warning(f"No details found for song ID: {song_id}")
            return None
        
        song_data = response.get("response", {}).get("song", {})
        logger.info(f"Retrieved details for song: {song_data.get('title', 'Unknown')}")
        return song_data
    
    def get_song_annotations(self, song_id: int) -> List[Dict]:
        """Get all annotations for a song by fetching referents"""
        logger.info(f"Getting annotations for song ID: {song_id}")
        
        all_annotations = []
        page = 1
        
        while True:
            params = {
                "song_id": song_id,
                "text_format": "plain",
                "per_page": 50,
                "page": page
            }
            
            response = self._make_request("/referents", params)
            if not response:
                logger.warning(f"No response for annotations page {page} of song {song_id}")
                break
            
            referents = response.get("response", {}).get("referents", [])
            if not referents:
                logger.info(f"No more annotations found at page {page}")
                break
            
            # Extract annotations from referents
            for referent in referents:
                for annotation in referent.get("annotations", []):
                    all_annotations.append({
                        "id": annotation.get("id"),
                        "body": annotation.get("body", {}).get("plain", ""),
                        "fragment": referent.get("fragment", ""),
                        "url": annotation.get("url"),
                        "votes_total": annotation.get("votes_total", 0),
                        "verified": annotation.get("verified", False),
                        "author": annotation.get("authors", [{}])[0].get("name", "Unknown") if annotation.get("authors") else "Unknown"
                    })
            
            logger.info(f"Found {len(referents)} referents on page {page}")
            page += 1
            
            # Check if we've reached the last page
            if page > response.get("meta", {}).get("last_page", 1):
                break
        
        logger.info(f"Total annotations found for song {song_id}: {len(all_annotations)}")
        return all_annotations
    
    def _format_lyrics(self, lyrics: str) -> str:
        """Clean and format scraped lyrics"""
        # Remove metadata and non-lyric content from the beginning
        lines = lyrics.split('\n')
        clean_lines = []
        lyrics_started = False
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and metadata
            if not line:
                if lyrics_started:
                    clean_lines.append('')
                continue
            
            # Skip contributor/translation info
            if any(word in line for word in ['Contributors', 'Translations', 'Nederlands', 'Türkçe', 'Español', 'Read More']):
                continue
            
            # Skip song title repetition at the end
            if line.endswith(' Lyrics') and len(line.split()) <= 3:
                continue
            
            # Start capturing lyrics when we hit verse/chorus markers or actual lyric content
            if any(marker in line for marker in ['[Verse', '[Chorus', '[Bridge', '[Outro', '[Intro', '[Pre-', '[Post-']) or lyrics_started:
                lyrics_started = True
                clean_lines.append(line)
            elif lyrics_started and line and not any(skip_word in line.lower() for skip_word in ['read more', 'embed', 'you might also like']):
                clean_lines.append(line)
        
        # Join and clean up formatting
        cleaned_lyrics = '\n'.join(clean_lines)
        
        # Clean up formatting
        cleaned_lyrics = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_lyrics)  # Multiple newlines to double
        cleaned_lyrics = re.sub(r'[ \t]+', ' ', cleaned_lyrics)  # Multiple spaces to single
        cleaned_lyrics = re.sub(r'\n ', '\n', cleaned_lyrics)  # Remove leading spaces
        cleaned_lyrics = re.sub(r' \n', '\n', cleaned_lyrics)  # Remove trailing spaces
        
        # Remove common Genius artifacts
        artifacts = [
            r'\d+Embed$',
            r'You might also like',
            r'See .* LiveGet tickets as low as \$\d+',
            r'ContributorsTranslations.*?Lyrics',
            r'On ".*?" the .* track off.*?Read More'
        ]
        for pattern in artifacts:
            cleaned_lyrics = re.sub(pattern, '', cleaned_lyrics, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        return cleaned_lyrics.strip()
    
    def get_song_lyrics_with_annotations(self, song_id: int) -> Optional[Song]:
        """Get complete song information including lyrics and annotations"""
        logger.info(f"Getting complete song data for ID: {song_id}")
        
        # Get song details
        song_details = self.get_song_details(song_id)
        if not song_details:
            return None
        
        metadata = self._extract_song_metadata(song_details)
        annotations = self.get_song_annotations(song_id)
        
        # Scrape lyrics
        lyrics_url = song_details.get("url", "")
        lyrics = self._scrape_lyrics(lyrics_url) if lyrics_url else None
        
        # Create Song object
        song = Song(
            id=song_id,
            title=song_details.get("title", ""),
            artist=song_details.get("primary_artist", {}).get("name", ""),
            album=metadata['album'],
            genre=metadata['genre'],
            release_year=metadata['release_year'],
            lyrics=lyrics,
            lyrics_url=lyrics_url,
            annotations=[f"{ann['fragment']}: {ann['body']}" for ann in annotations if ann.get('body')]
        )
        
        logger.info(f"Created Song object with {len(song.annotations)} annotations for: {song.title}")
        return song
