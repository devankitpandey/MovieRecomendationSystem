from typing import Dict, Any

import requests

from config.config import TMDB_API_KEY, TMDB_BASE_URL

HEADERS = {
    "Authorization": f"Bearer {TMDB_API_KEY}",
    "Content-Type": "application/json;charset=utf-8"
}

def _get(path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    url = f"{TMDB_BASE_URL}{path}"
    resp = requests.get(url, headers=HEADERS, params=params or {}, timeout=10)
    resp.raise_for_status()
    return resp.json()

def discover_movies(params: Dict[str, Any]) -> Dict[str, Any]:
    return _get("/discover/movie", params)

def get_movie_details(movie_id: int) -> Dict[str, Any]:
    return _get(f"/movie/{movie_id}", {"append_to_response": "credits"})

def get_trending_movies(selected_region:str = "IN"):
    return _get(f"/movie/now_playing?page=1&region={selected_region}",{})

def get_watch_providers(movie_id: int) -> Dict[str, Any]:
    return _get(f"/movie/{movie_id}/watch/providers").get("results", {})