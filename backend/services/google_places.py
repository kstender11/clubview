import requests
from core.config import get_settings
from services.cache import get_or_set
from core.rate_limiter import is_allowed
from services.foursquare import enrich_with_foursquare

cfg = get_settings()

def _fetch_nearby(lat, lng, radius=2000):
    if not cfg.APIS_ENABLED or not is_allowed("google"):
        return []

    url = (
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lng}&radius={radius}&type=night_club|bar"
        f"&key={cfg.GOOGLE_KEY}"
    )
    response = requests.get(url, timeout=8).json()
    google_results = response.get("results", [])

    enriched_results = []
    for place in google_results:
        name = place.get("name")
        location = place.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")

        # Add Foursquare enrichment
        fsq_data = enrich_with_foursquare(name, lat, lng)

        place["foursquare_id"] = fsq_data.get("foursquare_id")
        place["categories"] = fsq_data.get("categories")
        place["website"] = fsq_data.get("website")
        place["popularity"] = fsq_data.get("popularity")

        enriched_results.append(place)

    return enriched_results

def get_google_venues(lat: float, lng: float, radius=2000):
    return get_or_set(
        "google_nearby",
        {"lat": lat, "lng": lng, "r": radius},
        cfg.CACHE_TTL_HOURS,
        lambda: _fetch_nearby(lat, lng, radius)
    )
