import requests
from core.config import get_settings

cfg = get_settings()

def enrich_with_foursquare(fsq_id: str) -> dict:
    base_url = f"https://api.foursquare.com/v3/places/{fsq_id}"
    headers = {
        "Authorization": cfg.FOURSQUARE_API_KEY,
        "Accept": "application/json"
    }

    try:
        # Fetch place details
        detail_resp = requests.get(base_url, headers=headers, timeout=8)
        detail_data = detail_resp.json() if detail_resp.status_code == 200 else {}

        # Fetch tips (optional, often empty)
        tips_url = f"{base_url}/tips?limit=3&sort=POPULAR"
        tips_resp = requests.get(tips_url, headers=headers, timeout=8)
        tips_data = tips_resp.json() if tips_resp.status_code == 200 else []

        return {
            "website": detail_data.get("website"),
            "rating": detail_data.get("rating"),
            "popularity": detail_data.get("popularity"),
            "likes": detail_data.get("stats", {}).get("totalLikes"),
            "categories": [cat.get("name") for cat in detail_data.get("categories", [])],
            "tips": [tip.get("text") for tip in tips_data if "text" in tip],
            "summary": detail_data.get("description") or None
        }

    except Exception as e:
        print(f"Foursquare enrichment error: {e}")
        return {}
