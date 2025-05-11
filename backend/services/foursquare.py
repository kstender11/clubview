# foresquare.py (updated)
import requests
from core.config import get_settings

cfg = get_settings()

# Foursquare category IDs for bars/clubs
NIGHTLIFE_CATEGORY_IDS = {
    '4bf58dd8d48988d116941735',  # Bar
    '4bf58dd8d48988d11f941735',  # Nightclub
    '52e81612bcbc57f1066b7a0d',  # Cocktail Bar
    '4bf58dd8d48988d11e941735',  # Lounge
    '52e81612bcbc57f1066b79ed',  # Karaoke Bar
    '4bf58dd8d48988d120941735',  # Strip Club
    '56aa371be4b08b9a8d57355a',  # Speakeasy
    '4bf58dd8d48988d1d6941735'   # Dive Bar
}

def enrich_with_foursquare(fsq_id: str) -> dict:
    base_url = f"https://api.foursquare.com/v3/places/{fsq_id}"
    headers = {"Authorization": cfg.FOURSQUARE_API_KEY}
    
    try:
        detail_resp = requests.get(base_url, headers=headers, timeout=8)
        detail_data = detail_resp.json() if detail_resp.ok else {}
        
        # Extract category IDs for validation
        categories = detail_data.get("categories", [])
        category_ids = {cat["id"] for cat in categories}
        
        return {
            "is_nightlife": len(category_ids & NIGHTLIFE_CATEGORY_IDS) > 0,
            "categories": [cat.get("name") for cat in categories],
            "category_ids": list(category_ids),
            "website": detail_data.get("website"),
            "rating": detail_data.get("rating"),
            "popularity": detail_data.get("popularity"),
            "social_media": detail_data.get("social_media", {}),
            "description": detail_data.get("description", "")
        }
    except Exception as e:
        print(f"Foursquare error: {e}")
        return {"is_nightlife": False}