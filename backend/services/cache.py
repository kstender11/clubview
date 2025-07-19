from services.redis_cache import get_or_set

@router.get("/venues/discover")
def discover_venues(
    city: str,
    lat: float,
    lng: float,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
):
   def load_from_firestore():
    venues_ref = db.collection("venues").where("city", "==", city)  # 👈 new flat structure
    docs = venues_ref.stream()
    all_venues = []
    for doc in docs:
        data = doc.to_dict()
        venue_coords = data.get("location", {}).get("lat"), data.get("location", {}).get("lng")
            if None in venue_coords:
                continue
            if category and category.lower() not in " ".join(data.get("categories", [])).lower():
                continue
            dist_meters = geodesic((lat, lng), venue_coords).meters
            data["distance"] = dist_meters
            all_venues.append(data | {"id": doc.id})
        return all_venues

    params = {
        "city": city.strip().lower(),
        "lat": round(lat, 3),  # keep hash stable
        "lng": round(lng, 3),
        "category": category or None
    }

    all_venues = get_or_set("venues", params, ttl_hours=6, loader=load_from_firestore)
    return all_venues[skip: skip + limit]
