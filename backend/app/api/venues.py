from fastapi import APIRouter
from typing import Optional
from services.firestore_utils import db
from services.redis_cache import get_or_set  # ✅ make sure this import is working
from geopy.distance import geodesic

router = APIRouter()

@router.get("/venues/discover")
def discover_venues(
    city: str,
    lat: float,
    lng: float,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
):
    # Round location for cache key stability
    rounded_lat = round(lat, 3)
    rounded_lng = round(lng, 3)

    params = {
        "city": city.strip().lower(),
        "lat": rounded_lat,
        "lng": rounded_lng,
        "category": category or ""
    }

    def load_from_firestore():
        venues_ref = db.collection("cities").document(city).collection("venues")
        docs = (
            venues_ref
            .select(["name", "location", "categories"])  # ✅ optimized field selection
            .order_by("name")                            # ✅ needed for offset
            .stream()
        )

        user_coords = (lat, lng)
        all_venues = []

        for doc in docs:
            data = doc.to_dict()
            venue_coords = data.get("location", {}).get("lat"), data.get("location", {}).get("lng")
            if None in venue_coords:
                continue
            if category and category.lower() not in " ".join(data.get("categories", [])).lower():
                continue
            dist_meters = geodesic(user_coords, venue_coords).meters
            data["distance"] = dist_meters
            all_venues.append(data | {"id": doc.id})

        # Sort by distance after calculating it
        all_venues.sort(key=lambda v: v["distance"])
        return all_venues

    # Use Redis to cache this query result
    all_venues = get_or_set("venues", params, ttl_hours=3, loader=load_from_firestore)

    # Slice the cached result for pagination
    return all_venues[skip : skip + limit]
