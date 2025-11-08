import os
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY","")
TMDB_BASE_URL="https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL="https://image.tmdb.org/t/p/w500"

# Ollama
MODEL_HOST=os.getenv("MODEL_HOST")
MODEL_NAME=os.getenv("MODEL_NAME")

# Embedding Model
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)




# --- TMDB region codes (ISO 3166-1 alpha-2)
tmdb_regions = {
    "United States": "US",
    "India": "IN",
    "United Kingdom": "GB",
    "Canada": "CA",
    "Australia": "AU",
    "France": "FR",
    "Germany": "DE",
    "Japan": "JP",
    "South Korea": "KR",
    "Brazil": "BR",
    "Mexico": "MX",
    "Spain": "ES",
    "Italy": "IT",
    "Russia": "RU",
    "China": "CN",
    "Indonesia": "ID",
    "Turkey": "TR",
    "Argentina": "AR",
    "South Africa": "ZA",
    "Singapore": "SG"
}

# Minimal but practical TMDB genre mapping (keep extendable).
GENRE_NAME_TO_ID = {
  "action": 28,
  "adventure": 12,
  "animation": 16,
  "comedy": 35,
  "crime": 80,
  "documentary": 99,
  "drama": 18,
  "family": 10751,
  "fantasy": 14,
  "history": 36,
  "horror": 27,
  "music": 10402,
  "mystery": 9648,
  "romance": 10749,
  "science fiction": 878,
  "tv movie": 10770,
  "thriller": 53,
  "war": 10752,
  "western": 37,
  "action & adventure": 10759,
  "kids": 10762,
  "news": 10763,
  "reality": 10764,
  "sci-fi & fantasy": 10765,
  "soap": 10766,
  "talk": 10767,
  "war & politics": 10768
}
