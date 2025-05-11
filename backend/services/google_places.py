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
    
    try:
        response = requests.get(url, timeout=8).json()
        google_results = response.get("results", [])
        
        enriched_results = []
        for place in google_results:
            # Get Foursquare ID from Google's metadata if available
            fsq_id = place.get("external_ids", {}).get("foursquare")
            
            # Fallback: Search Foursquare using name + coordinates
            if not fsq_id:
                fsq_data = enrich_with_foursquare(
                    name=place.get("name"),
                    lat=place["geometry"]["location"]["lat"],
                    lng=place["geometry"]["location"]["lng"]
                )
                fsq_id = fsq_data.get("foursquare_id")

            if fsq_id:
                place["foursquare_id"] = fsq_id
                place["categories"] = fsq_data.get("categories")
                place["is_nightlife"] = fsq_data.get("is_nightlife", False)
                
                enriched_results.append(place)

        return enriched_results

    except Exception as e:
        print(f"Google Places error: {e}")
        return []

def get_google_venues(lat: float, lng: float, radius=2000):
    return get_or_set(
        "google_nearby",
        {"lat": lat, "lng": lng, "r": radius},
        cfg.CACHE_TTL_HOURS,
        lambda: _fetch_nearby(lat, lng, radius)
    )