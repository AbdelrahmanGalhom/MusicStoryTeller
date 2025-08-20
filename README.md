# Music Storyteller

> Transform songs into captivating stories using AI-powered natural language processing

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.27-orange.svg)](https://langchain.com)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-AI-red.svg)](https://gemini.google.com)

## Overview & Problem Statement

Music Storyteller transforms song lyrics and metadata into engaging narratives using AI-powered natural language processing. Current music analysis tools focus on technical aspects rather than extracting semantic meaning, creating gaps for content creators, educators, and entertainment platforms seeking narrative-based content from musical sources.

## Architecture & Implementation

The system employs a three-tier architecture combining the Genius API for song data extraction, Google Gemini via LangChain for story generation, and FastAPI for service delivery. Key technical features include:

```
Client Applications ◄──► FastAPI Gateway ◄──► AI Services (Gemini/LangChain)
                                 │
                                 ▼
                         External APIs (Genius)
```

**Core Capabilities:**
- **Data Integration**: Combines lyrics, artist information, and metadata from multiple sources
- **AI Processing**: Custom prompt engineering for contextually relevant story generation  
- **API Design**: RESTful endpoints with auto-generated documentation and type safety
- **Production Features**: Health monitoring, error handling, and horizontal scalability

## Technology Stack

### Backend Framework
- **FastAPI**: Modern, high-performance web framework for building APIs
- **Uvicorn**: Lightning-fast ASGI server for production deployment

### AI & Machine Learning
- **LangChain**: Framework for developing applications with large language models
- **Google Gemini**: State-of-the-art generative AI for natural language processing

### Data Processing
- **Pydantic**: Data validation using Python type annotations
- **Beautiful Soup**: Web scraping and HTML parsing for lyrics extraction
- **Requests**: HTTP library for external API integration


## Project Structure

```
MusicStoryTeller/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── routes/
│   │   │   ├── song_routes.py   # Song search and retrieval endpoints
│   │   │   └── story_routes.py  # Story generation endpoints
│   │   └── schemas/
│   │       ├── song_schemas.py  # Song data models
│   │       └── story_schemas.py # Story data models
│   ├── services/
│   │   ├── genius_service.py    # Genius API integration
│   │   └── langchain_service.py # AI story generation service
│   ├── models/
│   │   ├── song.py             # Song entity models
│   │   └── story.py            # Story entity models
│   └── helpers/
│       └── config.py           # Configuration management
├── requirements.txt            # Python dependencies
├── README.md                  # Project documentation
└── LICENSE                    # Project license
```

## Getting Started

### Prerequisites
- Python 3.11 or later
- Google Gemini API key
- Genius API key

### Environment Setup

1. **Create and activate a conda environment:**
```bash
conda create -n music-storyteller python=3.11
conda activate music-storyteller
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp src/.env.example src/.env
```

Edit `src/.env` and add your API keys:
```env
GEMINI_API_KEY=your_google_gemini_api_key
GENIUS_API_KEY=your_genius_api_key
```

### Running the Application

```bash
cd src
uvicorn main:app --reload --port 7000
```

The API will be available at `http://localhost:7000`

## API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/stories/generate` | Generate a story from a song |
| `GET` | `/api/v1/stories/health` | Health check for story services |
| `POST` | `/api/v1/songs/search` | Search for songs by title/artist |
| `GET` | `/api/v1/songs/{song_id}` | Get detailed song information |
| `GET` | `/health` | Overall application health check |

### Interactive Documentation
Visit `http://localhost:7000/docs` for comprehensive API documentation with interactive testing capabilities.

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest new features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Developed by Abdelrahman Galhom**

*Advanced AI-powered system for transforming musical content into narrative stories*
