from fastapi import APIRouter
from typing import Optional
from services.firestore_utils import db
from geopy.distance import geodesic

router = APIRouter()

@router.get("/venues/discover")
def discover_venues(
    city: str,
    lat: float,
    lng: float,
    category: Optional[str] = None,
    limit: int = 20,
):
    venues_ref = db.collection("cities").document(city).collection("venues")
    docs = venues_ref.stream()

    user_coords = (lat, lng)
    venues = []

    for doc in docs:
        data = doc.to_dict()
        venue_coords = (
            data.get("location", {}).get("lat"),
            data.get("location", {}).get("lng")
        )

        if None in venue_coords:
            continue

        # Optional category filter
        if category and category.lower() not in " ".join(data.get("categories", [])).lower():
            continue

        # Distance from user
        dist_meters = geodesic(user_coords, venue_coords).meters
        data["distance"] = dist_meters
        venues.append(data | {"id": doc.id})

    # Sort by distance
    venues.sort(key=lambda v: v["distance"])

    return venues[:limit]
