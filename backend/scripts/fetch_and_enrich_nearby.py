#!/usr/bin/env python3
"""
scripts/fetch_and_enrich_nearby.py
Simplified version using Google's native type filtering and stricter legitimacy checks.
"""
import argparse, time, requests, firebase_admin
from datetime import datetime, timedelta, UTC
from math import radians, sin, cos, sqrt, atan2
from typing import Dict, Any
from firebase_admin import credentials, firestore, initialize_app

from core.config          import get_settings
from scripts.add_fsq_ids   import fetch_fsq_id
from scripts.add_hours     import get_google_hours
from scripts.add_instagram import find_instagram_link
from services.foursquare   import enrich_with_foursquare

cfg = get_settings()

# ──────────────────────── Helpers ─────────────────────────
def distance_m(lat1, lng1, lat2, lng2):
    R = 6_371_000
    dlat, dlng = radians(lat2-lat1), radians(lng2-lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    return int(2*R*atan2(sqrt(a), sqrt(1-a)))

def get_google_details(place_id: str) -> Dict[str, Any]:
    url = ("https://maps.googleapis.com/maps/api/place/details/json"
           f"?place_id={place_id}&fields=website,editorial_summary"
           f"&key={cfg.GOOGLE_KEY}")
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
    url = ("https://maps.googleapis.com/maps/api/place/nearbysearch/json"
           f"?location={lat},{lng}&radius={radius}"
           f"&type=bar|night_club"
           f"&key={cfg.GOOGLE_KEY}")
    results, token = [], None
    while len(results) < limit:
        res = requests.get(url + (f"&pagetoken={token}" if token else ""), timeout=10).json()
        results.extend(res.get("results", []))
        token = res.get("next_page_token")
        if not token:
            break
        time.sleep(2)
    return results[:limit]

# ─────────────────── Simplify record ─────────────────────
def simplify(place: Dict[str, Any], user_lat: float, user_lng: float) -> Dict[str, Any]:
    loc = place.get("geometry", {}).get("location", {})
    v_lat, v_lng = loc.get("lat"), loc.get("lng")

    # Inference for city/state
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


# ────────────── Simple legitimacy check ─────────────────────
def is_legit_bar(g_types: list[str], fsq_cats: list[str] = [], name: str = "") -> bool:
    EXCLUDES = {"restaurant", "cafe", "bbq", "pizza", "steakhouse", "breakfast", "hotel"}
    all_text = " ".join(g_types + fsq_cats + [name]).lower()
    if any(x in all_text for x in EXCLUDES):
        return False
    return any(x in g_types for x in ("bar", "night_club"))

# ────────────── Main enrichment ─────────────────────
FSQ_COOLDOWN = timedelta(days=7)

def upsert_and_enrich(doc: Dict[str, Any]):
    pid = doc["place_id"]
    ref = db.collection("venues").document(pid)
    snap = ref.get()

    if not snap.exists:
        ref.set(doc)
        print(f"➕ Added {doc['name']}")
        data = doc
    else:
        data = snap.to_dict()
        print(f"↻ Found existing {data['name']}")

    if not is_legit_bar(data.get("types", []), data.get("categories", []), data.get("name")):
        return

    # Foursquare ID
    if not data.get("foursquare_id"):
        loc = data.get("location", {})
        fsq = fetch_fsq_id(data["name"], loc.get("lat"), loc.get("lng"))
        if fsq:
            ref.update({"foursquare_id": fsq})
            data["foursquare_id"] = fsq
            print(f"   • added Foursquare ID {fsq}")

    # Foursquare enrichment (only if missing or stale)
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
    p = argparse.ArgumentParser()
    p.add_argument("lat", type=float)
    p.add_argument("lng", type=float)
    p.add_argument("--radius", type=int, default=3000)
    args = p.parse_args()

    print("🔍 Fetching Google Places …")
    places = fetch_google_nearby(args.lat, args.lng, args.radius)
    print(f"📑 Received {len(places)} Google results\n")

    for place in places:
        simplified = simplify(place, args.lat, args.lng)
        if is_legit_bar(simplified["types"], simplified["categories"], simplified["name"]):
            upsert_and_enrich(simplified)
            time.sleep(0.2)

    print("\n✅ Finished fetching & enriching.")

if __name__ == "__main__":
    main()
