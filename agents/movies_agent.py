from operator import index
from typing import List, Dict

import numpy as np

from agents.indexing_agent import build_llamaIndex_for_spec
from agents.query_agent import build_search_spec
from config.config import TMDB_IMAGE_BASE_URL
from tmdb_services.where_to_watch import get_where_to_watch


def get_movies_recommendations(query:str = "", region:str = 'IN', size:int = 6):
    # 1. Build structured TMDB spec via LangChain LLM
    spec = build_search_spec(query)

    # 2. Build FAISS index + enriched movies + embed_model
    faiss_index, movies, embed_model = build_llamaIndex_for_spec(spec)

    if not movies:
        return []

    # 3. Embed the original query
    q_emb = embed_model.get_text_embedding(query)
    q_vec = np.asarray([q_emb], dtype="float32")
    q_vec = np.ascontiguousarray(q_vec, dtype="float32")

    # 4. Run FAISS similarity search
    k = min(size, len(movies))
    distances, indices = faiss_index.search(q_vec, k)

    # 5. Build response objects
    results: List[Dict] = []
    for idx in indices[0]:
        movie = movies[idx]
        wp = get_where_to_watch(movie["id"], movie["title"])

        results.append({
            "id": movie["id"],
            "title": movie["title"],
            "overview": movie["overview"],
            "genres": movie["genres"],
            "language": movie["language"],
            "vote_average": movie["vote_average"],
            "release_date": movie["release_date"],
            "poster_url": (
                f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}"
                if movie.get("poster_path") else None
            ),
            "where_to_watch": wp.dict(),
        })

    return results