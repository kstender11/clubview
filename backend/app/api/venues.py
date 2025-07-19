from fastapi import APIRouter
from typing import Optional
from services.firestore_utils import db
from services.redis_cache import get_or_set
from geopy.distance import geodesic

router = APIRouter()

@router.get("/venues/discover")
def discover_venues(
    lat: float,
    lng: float,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
):
    # Round for cache key stability
    rounded_lat = round(lat, 3)
    rounded_lng = round(lng, 3)

    params = {
        "lat": rounded_lat,
        "lng": rounded_lng,
        "category": category or ""
    }

    def load_from_firestore():
        venues_ref = db.collection("venues")
        docs = (
            venues_ref
            .select(["name", "location", "categories", "city"])
            .order_by("name")
            .stream()
        )

        user_coords = (lat, lng)  # ✅ use the full-precision user location
        nearby = []

        for doc in docs:
            data = doc.to_dict()
            venue_coords = data.get("location", {}).get("lat"), data.get("location", {}).get("lng")
            if None in venue_coords:
                continue
            if category and category.lower() not in " ".join(data.get("categories", [])).lower():
                continue
            dist_meters = geodesic(user_coords, venue_coords).meters
            if dist_meters > 48280:  # ~30 miles
                continue
            data["distance"] = dist_meters
            nearby.append(data | {"id": doc.id})

        nearby.sort(key=lambda v: v["distance"])
        return nearby
    
    all_venues = load_from_firestore()
    return all_venues[skip : skip + limit]
