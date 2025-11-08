import json
import os
from typing import Dict, List

import faiss
import numpy as np

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from sentence_transformers import SentenceTransformer

from config.config import GENRE_NAME_TO_ID, EMBEDDING_MODEL_NAME, MODEL_HOST, MODEL_NAME
from models.models import TMDBSearchSpec
from tmdb_services.tmdb_service import discover_movies, get_movie_details


# Global Hugging face mode
# We'll store the model inside your project to avoid the llama_index Cache issue
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_MODEL_DIR = os.path.join(BASE_DIR, "models", "all-MiniLM-L6-v2")

os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)

# If the model directory is empty or missing config, download & save once
config_path = os.path.join(LOCAL_MODEL_DIR, "config_sentence_transformers.json")
if not os.path.exists(config_path):
    # Download from HF via sentence-transformers and save a full copy
    st_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    st_model.save(LOCAL_MODEL_DIR)

# Now use this stable local directory for LlamaIndex embeddings
embed_model = HuggingFaceEmbedding(model_name=LOCAL_MODEL_DIR)

def gener_to_ids(include_genres):
    ids = []
    for genr in include_genres:
        if genr.strip().lower() in GENRE_NAME_TO_ID :
            ids.append(GENRE_NAME_TO_ID[genr])

    return ",".join(map(str,ids)) if ids else None


def build_quser_params(spec):
    params: Dict[str , str] = {
        "sort_by" : spec.sort_by,
        "include_adult" : spec.adult,
        "include_video" : "false",
        "page": "1"
    }
    # Language
    if spec.language :
        params["with_original_language"] = spec.language.lower()

    # Region
    if spec.region :
        params["region"] = spec.region.upper()

    # Geners
    included_geners = gener_to_ids(spec.include_genres)
    excluded_geners = gener_to_ids(spec.exclude_genres)


    if included_geners :
        params["with_genres"] = included_geners

    if excluded_geners :
        params["without_genres"] = excluded_geners

    # Release date

    if spec.min_year:
        params["primary_release_date.gte"] = f"{spec.min_year}-01-01"

    if spec.max_year:
        params["primary_release_date.lte"] = f"{spec.max_year}-12-31"


    # Voting
    if spec.min_vote_average :
        params["vote_average.gte"] = str(spec.min_vote_average)

    if spec.max_vote_average :
        params["vote_average.lte"] = str(spec.max_vote_average)

    return params


def fetch_movies_for_specs(spec):
    query_param = build_quser_params(spec)
    print(f"query_param :: {query_param}")

    movies_results: List[Dict] = []
    pages = spec.discover_limit
    page_num = 1
    while pages > 0 :
        query_param["page"] = str(page_num)
        data = discover_movies(query_param)
        results = data.get("results",[])
        if not results:
            break

        slice = results[:pages]
        movies_results.extend(slice)
        pages -= len(slice)
        page_num+=1

    return movies_results


def enrich_data(movie):
    movie_details = get_movie_details(movie["id"])
    genres = [ g["name"] for g in movie_details.get("genres",[]) ]
    overview = movie_details.get("overview","") or movie.get("overview","") or ""
    return {
        "id": movie_details["id"],
        "title": movie_details.get("title") or movie.get("title"),
        "overview": overview,
        "genres": genres,
        "language": movie_details.get("original_language"),
        "vote_average": movie_details.get("vote_average"),
        "popularity": movie_details.get("popularity"),
        "release_date": movie_details.get("release_date"),
        "poster_path": movie_details.get("poster_path") or movie.get("poster_path"),
    }


def build_llamaIndex_for_spec(spec:TMDBSearchSpec):

    # Get list of Movies from TMDB
    movies_list = fetch_movies_for_specs(spec)

    # Get movies details and populate list

    enriched_data_movies = [ enrich_data(movie) for movie in movies_list ]
    print(f"enriched_data_movies {enriched_data_movies}")
    indexing_docs = []
    for m in enriched_data_movies:
        text = (
            f"Title: {m['title']}\n"
            f"Overview: {m['overview']}\n"
            f"Genres: {', '.join(m['genres'])}\n"
            f"Language: {m['language']}\n"
            f"Rating: {m['vote_average']}\n"
            f"Release Date: {m['release_date']}"
        )
        indexing_docs.append(text)



    # Creating FAISS llama index
    embeddins = embed_model.get_text_embedding_batch(indexing_docs)
    # Convert to proper 2D float32 contiguous array
    emb_array = np.asarray(embeddins, dtype="float32")
    if emb_array.ndim != 2:
        raise ValueError(f"Expected 2D embeddings, got shape {emb_array.shape}")
    emb_array = np.ascontiguousarray(emb_array, dtype="float32")

    n, dim = emb_array.shape

    # --- Step 5: Build FAISS index in the correct way ---
    index = faiss.IndexFlatL2(dim)  # L2 distance flat index
    index.add(emb_array)  # ✅ this is correct for faiss-cpu

    return index,enriched_data_movies,embed_model