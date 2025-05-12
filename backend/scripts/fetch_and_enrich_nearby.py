#!/usr/bin/env python3
"""
scripts/fetch_and_enrich_nearby.py
Fetch Google venues and enrich with Foursquare, only storing validated nightlife spots.
"""

import argparse, time, requests, firebase_admin
from datetime import datetime, timedelta, UTC
from math import radians, sin, cos, sqrt, atan2
from typing import Dict, Any
from firebase_admin import credentials, firestore, initialize_app

from core.config import get_settings
from scripts.add_fsq_ids import fetch_fsq_id
from scripts.add_hours import get_google_hours
from scripts.add_instagram import find_instagram_link
from services.foursquare import enrich_with_foursquare
from services.venue_validation import validate_venue  # ✅ Added robust validator

cfg = get_settings()

# ──────────────────────── Helpers ─────────────────────────
def distance_m(lat1, lng1, lat2, lng2):
    R = 6_371_000
    dlat, dlng = radians(lat2-lat1), radians(lng2-lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    return int(2*R*atan2(sqrt(a), sqrt(1-a)))

def get_google_details(place_id: str) -> Dict[str, Any]:
    url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&fields=website,editorial_summary"
        f"&key={cfg.GOOGLE_KEY}"
    )
    try:
        res = requests.get(url, timeout=10).json()
        r = res.get("result", {})
        return {
            "website": r.get("website"),
            "summary": r.get("editorial_summary", {}).get("overview")
        }
    except Exception:
        return {}

# ──────────────────────── Firestore ─────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)
db = firestore.client()

# ───────────────────── Google Places API ─────────────────────
def fetch_google_nearby(lat: float, lng: float, radius: int = 3000, limit: int = 60):
    url = (
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lng}&radius={radius}&type=bar|night_club"
        f"&key={cfg.GOOGLE_KEY}"
    )
    results, token = [], None
    while len(results) < limit:
        res = requests.get(url + (f"&pagetoken={token}" if token else ""), timeout=10).json()
        results.extend(res.get("results", []))
        token = res.get("next_page_token")
        if not token:
            break
        time.sleep(2)
    return results[:limit]

# ────────────── Simplify record ─────────────────────
def simplify(place: Dict[str, Any], user_lat: float, user_lng: float) -> Dict[str, Any]:
    loc = place.get("geometry", {}).get("location", {})
    v_lat, v_lng = loc.get("lat"), loc.get("lng")

    if 33.5 < v_lat < 34.5 and -119 < v_lng < -117:
        city = "Los Angeles"
        state = "CA"
    elif 37.5 < v_lat < 38.5 and -123 < v_lng < -121:
        city = "San Francisco"
        state = "CA"
    else:
        city = "Unknown"
        state = "Unknown"

    return {
        "name": place.get("name"),
        "address": place.get("vicinity"),
        "place_id": place.get("place_id"),
        "rating": place.get("rating"),
        "price_level": place.get("price_level"),
        "types": place.get("types", []),
        "location": {"lat": v_lat, "lng": v_lng},
        "distance": distance_m(user_lat, user_lng, v_lat, v_lng),
        "foursquare_id": None,
        "categories": [],
        "summary": None,
        "website": None,
        "instagram_url": None,
        "hours": None,
        "city": city,
        "state": state,
    }

# ────────────── Main enrichment ─────────────────────
FSQ_COOLDOWN = timedelta(days=7)

def upsert_and_enrich(doc: Dict[str, Any], city: str):
    pid = doc["place_id"]
    ref = db.collection("cities").document(city).collection("venues").document(pid)
    snap = ref.get()

    # Only add if not already in DB
    if not snap.exists:
        # ❗ Validate before saving
        if not validate_venue(doc):
            print(f"🚫 Skipping {doc['name']} — did not pass nightlife validation.")
            return

        ref.set(doc)
        print(f"✅ Added {doc['name']} after validation")
        data = doc
    else:
        data = snap.to_dict()

        # Re-validate existing data
        if not validate_venue(data):
            print(f"🚫 Skipping {data['name']} — existing doc failed validation.")
            return

        print(f"↻ Found existing {data['name']}")

    # ✅ Continue enrichment (only for valid docs)
    if not data.get("foursquare_id"):
        loc = data.get("location", {})
        fsq = fetch_fsq_id(data["name"], loc.get("lat"), loc.get("lng"))
        if fsq:
            ref.update({"foursquare_id": fsq})
            data["foursquare_id"] = fsq
            print(f"   • added Foursquare ID {fsq}")

    last = data.get("last_fsq_refresh")
    if data.get("foursquare_id") and (not last or datetime.now(UTC) - last > FSQ_COOLDOWN):
        enrich = enrich_with_foursquare(data["foursquare_id"])
        if enrich:
            enrich["last_fsq_refresh"] = datetime.now(UTC)
            ref.update(enrich)
            data.update(enrich)
            print("   • enriched from Foursquare")

    if not data.get("website") or not data.get("summary"):
        patch = get_google_details(pid)
        if patch:
            ref.update(patch)
            print("   • added website/summary from Google")

    if not data.get("hours"):
        hrs = get_google_hours(pid)
        if hrs:
            ref.update({"hours": hrs})
            print("   • added hours")

    if not data.get("instagram_url") and data.get("website"):
        insta = find_instagram_link(data["website"])
        if insta:
            ref.update({"instagram_url": insta})
            print("   • added Instagram")

# ────────────── Main CLI ─────────────────────
def main():
    radius = 3000
    total = 0

    for lat, lng in LA_GRID_COORDS:
        print(f"\n📍 Fetching at ({lat}, {lng}) with radius {radius}")
        places = fetch_google_nearby(lat, lng, radius)
        print(f"📑 Received {len(places)} results")

        for place in places:
            simplified = simplify(place, lat, lng)
            upsert_and_enrich(simplified, simplified["city"])
            total += 1
            time.sleep(0.2)

    print(f"\n✅ Finished populating LA with {total} venues enriched.")

LA_GRID_COORDS = [
    # Coastal / Westside
    (34.0219, -118.4814),  # Santa Monica Pier
    (33.9850, -118.4695),  # Venice Beach Boardwalk
    (34.0259, -118.7798),  # Malibu (Point Dume)
    (33.9783, -118.4519),  # Marina del Rey
    (34.0042, -118.4851),  # Ocean Park (Santa Monica)
    (34.0138, -118.4933),  # Downtown Santa Monica
    (34.0225, -118.3965),  # Culver City

    # Central LA
    (34.0635, -118.3581),  # West Hollywood (Sunset Strip)
    (34.0830, -118.3405),  # Hollywood & Vine
    (34.1016, -118.3380),  # Hollywood Sign Viewpoint
    (34.0901, -118.3616),  # Santa Monica & La Cienega (Barney’s Beanery)
    (34.0701, -118.3555),  # La Brea & Melrose
    (34.0614, -118.3442),  # Fairfax & Beverly (LACMA)

    # Downtown & Arts
    (34.0469, -118.2428),  # City Hall (DTLA Core)
    (34.0493, -118.2512),  # Walt Disney Concert Hall
    (34.0435, -118.2540),  # Arts District (DTLA)
    (34.0542, -118.2440),  # Little Tokyo
    (34.0476, -118.2375),  # Boyle Heights (Mariachi Plaza)

    # Eastside / Northeast
    (34.0800, -118.2000),  # Highland Park (Figueroa)
    (34.0847, -118.2123),  # Eagle Rock Plaza
    (34.0928, -118.2786),  # Echo Park Lake
    (34.1106, -118.2702),  # Silver Lake Reservoir

    # South LA / Basin
    (33.9617, -118.3531),  # SoFi Stadium (Inglewood)
    (33.9303, -118.4036),  # LAX Airport
    (33.9456, -118.2417),  # Compton Civic Center
    (33.9272, -118.2801),  # Watts Towers
    (33.7701, -118.1937),  # Long Beach Waterfront

    # Valley / Pasadena
    (34.1400, -118.1500),  # Pasadena City Hall
    (34.1478, -118.1445),  # Old Town Pasadena
    (34.1804, -118.3087),  # Burbank Media District
    (34.1869, -118.4483),  # Van Nuys Civic Center
    (34.2014, -118.5347),  # Chatsworth (Northwest Valley)

    # Universities / Cultural
    (34.0689, -118.4452),  # UCLA (Westwood)
    (34.0193, -118.2859),  # USC Campus
    (34.0780, -118.4741),  # Getty Center
    (34.0628, -118.3085),  # Koreatown (Wilshire & Western)
]


if __name__ == "__main__":
    main()
