from urllib.parse import quote_plus

from models.models import WatchProviderInfo
from tmdb_services.tmdb_service import get_watch_providers


def get_where_to_watch(movie_id: int, title: str, region:str = "IN") -> WatchProviderInfo:
    data = get_watch_providers(movie_id)
    region_data = data.get(region, {})

    info = WatchProviderInfo()

    if region_data:
        if region_data.get("flatrate"):
            info.stream = [p["provider_name"] for p in region_data["flatrate"]]
        if region_data.get("rent"):
            info.rent = [p["provider_name"] for p in region_data["rent"]]
        if region_data.get("buy"):
            info.buy = [p["provider_name"] for p in region_data["buy"]]

    if not (info.stream or info.rent or info.buy):
        info.fallback_url = (
            f"https://www.justwatch.com/{region.lower()}/search?q={quote_plus(title)}"
        )

    return info