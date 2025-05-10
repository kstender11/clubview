# services/firebase.py

from services.google_places import get_google_venues
from services.firestore_utils import add_venue_to_firestore
from services.foursquare import enrich_with_foursquare
from datetime import datetime
from typing import Dict, Any
from math import radians, cos, sin, sqrt, atan2

# Haversine formula to compute distance in km
def compute_distance_km(lat1, lng1, lat2, lng2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def simplify_venue(venue: Dict[str, Any], user_lat: float, user_lng: float, city: str = "Los Angeles") -> Dict[str, Any]:
    loc = venue.get("geometry", {}).get("location", {})
    lat = loc.get("lat")
    lng = loc.get("lng")

    if lat is None or lng is None:
        print(f"⚠️ Skipping venue due to missing location: {venue.get('name')}")
        return None  # skip this one

    distance = round(compute_distance_km(user_lat, user_lng, lat, lng) * 1000)  # in meters

    return {
        "name": venue.get("name"),
        "address": venue.get("vicinity"),
        "place_id": venue.get("place_id"),
        "rating": venue.get("rating"),
        "price_level": venue.get("price_level"),
        "types": venue.get("types"),
        "location": loc,
        "foursquare_id": venue.get("foursquare_id"),
        "categories": venue.get("categories"),
        "website": venue.get("website"),
        "popularity": venue.get("popularity"),
        "instagram_embed": venue.get("instagram_embed"),
        "created_at": datetime.utcnow().isoformat(),
        "city": city,
        "distance": distance
    }


def upload_venues_to_firebase(lat: float, lng: float, city: str = "Los Angeles"):
    venues = get_google_venues(lat, lng)
    for venue in venues:
        fsq_id = venue.get("foursquare_id")
        if fsq_id:
            enrichment = enrich_with_foursquare(fsq_id)
            venue.update(enrichment)
        simplified = simplify_venue(venue, user_lat=lat, user_lng=lng, city=city)
        if simplified:
            add_venue_to_firestore(simplified)

