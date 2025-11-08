from typing import Optional, List
from pydantic import BaseModel

class TMDBSearchSpec(BaseModel):
    include_genres: List[str] = []
    exclude_genres: List[str] = []
    language: Optional[str] = None
    region: Optional[str] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    min_vote_average: Optional[float] = None
    max_vote_average: Optional[float] = None
    sort_by: str = "popularity.desc"
    adult: bool = False
    discover_limit: int = 50   # how many movies to pull from /discover

class Movie(BaseModel):
    id: int
    title: str
    overview: Optional[str]
    genres: List[str]
    language: Optional[str]
    vote_average: Optional[float]
    popularity: Optional[float]
    release_date: Optional[str]
    poster_path: Optional[str]
    doc_text: str

class WatchProviderInfo(BaseModel):
    stream: List[str] = []
    rent: List[str] = []
    buy: List[str] = []
    fallback_url: Optional[str] = None
