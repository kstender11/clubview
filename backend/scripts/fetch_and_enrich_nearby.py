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
from services.venue_validation import validate_venue

cfg = get_settings()

# ──────────────────────── Helpers ─────────────────────────
def distance_m(lat1, lng1, lat2, lng2):
    R = 6_371_000
    dlat, dlng = radians(lat2 - lat1), radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return int(2 * R * atan2(sqrt(a), sqrt(1 - a)))

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
    elif 37.4 < v_lat < 37.5 and -122.3 < v_lng < -122.1:
        city = "Menlo Park"
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

    if not snap.exists:
        if not validate_venue(doc):
            print(f"🚫 Skipping {doc['name']} — did not pass nightlife validation.")
            return
        ref.set(doc)
        print(f"✅ Added {doc['name']} after validation")
        data = doc
    else:
        data = snap.to_dict()
        if not validate_venue(data):
            print(f"🚫 Skipping {data['name']} — existing doc failed validation.")
            return
        print(f"↻ Found existing {data['name']}")

    last = data.get("last_fsq_refresh")
    should_refresh_fsq = data.get("foursquare_id") and (not last or datetime.now(UTC) - last > FSQ_COOLDOWN)

    if not data.get("foursquare_id"):
        loc = data.get("location", {})
        fsq = fetch_fsq_id(data["name"], loc.get("lat"), loc.get("lng"))
        if fsq:
            ref.update({"foursquare_id": fsq})
            data["foursquare_id"] = fsq
            print(f"   • added Foursquare ID {fsq}")

    if data.get("foursquare_id") and should_refresh_fsq:
        enrichment = enrich_with_foursquare(data["foursquare_id"])
        if enrichment:
            enrichment["last_fsq_refresh"] = datetime.now(UTC)
            ref.update(enrichment)
            data.update(enrichment)
            print("   • enriched from Foursquare")

    if data.get("place_id") and (not data.get("website") or not data.get("summary")):
        gdata = get_google_details(data["place_id"])
        if gdata:
            ref.update(gdata)
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

# ────────────── CLI Entrypoint ─────────────────────
def main():
    radius = 3000
    total = 0

    for lat, lng in MENLO_GRID_COORDS:
        print(f"\n📍 Fetching at ({lat}, {lng}) with radius {radius}")
        places = fetch_google_nearby(lat, lng, radius)
        print(f"📑 Received {len(places)} results")

        for place in places:
            simplified = simplify(place, lat, lng)
            upsert_and_enrich(simplified, simplified["city"])
            total += 1
            time.sleep(0.2)

    print(f"\n✅ Finished populating Menlo Park with {total} venues enriched.")

MENLO_GRID_COORDS = [
    (37.4540, -122.1817),  # Downtown Menlo Park
    (37.4236, -122.1700),  # Stanford Shopping Center
    (37.4258, -122.1979),  # Sharon Heights
]

if __name__ == "__main__":
    main()
