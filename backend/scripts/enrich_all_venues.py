import requests
import time
import firebase_admin
from typing import Optional
from firebase_admin import credentials, firestore, initialize_app
from core.config import get_settings

cfg = get_settings()

# ─── Firebase Setup ─────────────────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)

db = firestore.client()

# ─── Google Enrichment ──────────────────────────────────────
def get_google_website_and_summary(place_id: str) -> dict:
    url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&fields=website,editorial_summary"
        f"&key={cfg.GOOGLE_KEY}"
    )
    try:
        res = requests.get(url, timeout=5)
        result = res.json().get("result", {})
        return {
            "website": result.get("website"),
            "summary": result.get("editorial_summary", {}).get("overview")
        }
    except Exception as e:
        print(f"❌ Google details error: {e}")
        return {}

# ─── Fallback Summary Generator ─────────────────────────────
def generate_fallback_summary(categories):
    if categories:
        if len(categories) == 1:
            return f"A {categories[0]} in downtown LA."
        elif len(categories) == 2:
            return f"A {categories[0]} and {categories[1]} in downtown LA."
        else:
            return f"A {categories[0]}, {categories[1]}, and more in downtown LA."
    return "A nightlife venue in downtown LA."

# ─── Foursquare Enrichment ──────────────────────────────────
def enrich_with_foursquare(fsq_id: str) -> dict:
    base_url = f"https://api.foursquare.com/v3/places/{fsq_id}"
    tips_url = f"{base_url}/tips"

    headers = {
        "Accept": "application/json",
        "Authorization": cfg.FOURSQUARE_API_KEY,
    }

    enrichment = {}

    # ✨ Step 1: Place Details
    try:
        res = requests.get(base_url, headers=headers, timeout=5)
        res.raise_for_status()
        data = res.json()

        enrichment["website"] = data.get("website")
        enrichment["categories"] = [cat["name"] for cat in data.get("categories", [])]
        enrichment["rating"] = data.get("rating")
        enrichment["popularity"] = data.get("popularity")

        stats = data.get("stats", {})
        if "totalLikes" in stats:
            enrichment["likes"] = stats["totalLikes"]
    except Exception as e:
        print(f"❌ Foursquare details error for {fsq_id}: {e}")

    # ✨ Step 2: Tips
    try:
        tips_res = requests.get(tips_url, headers=headers, timeout=5)
        tips_res.raise_for_status()
        tips_data = tips_res.json()

        # Some Foursquare responses return a list directly
        if isinstance(tips_data, list):
            tips = [t["text"] for t in tips_data if "text" in t]
        else:
            tips = [t["text"] for t in tips_data.get("tips", []) if "text" in t]

        if tips:
            enrichment["tips"] = tips[:3]
    except Exception as e:
        print(f"❌ Foursquare tips error for {fsq_id}: {e}")

    return enrichment

# ─── Main Enrichment Routine ────────────────────────────────
def enrich_all_venues(city: str = "Los Angeles"):
    print("🔍 Script started...")
    venues_ref = db.collection("cities").document(city).collection("venues")
    docs = list(venues_ref.stream())
    print(f"📦 Found {len(docs)} venues.")

    for doc in docs:
        data = doc.to_dict()
        fsq_id = data.get("foursquare_id")
        if not fsq_id:
            print(f"🚫 Skipping {data.get('name')} — no Foursquare ID.")
            continue

        enriched = enrich_with_foursquare(fsq_id)

        # Google summary/website fallback
        if data.get("place_id"):
            google_data = get_google_website_and_summary(data["place_id"])
            if not enriched.get("website") and google_data.get("website"):
                enriched["website"] = google_data["website"]
            if not enriched.get("summary") and google_data.get("summary"):
                enriched["summary"] = google_data["summary"]

        # Fallback summary if still missing
        if not enriched.get("summary"):
            enriched["summary"] = generate_fallback_summary(
                enriched.get("categories") or data.get("categories", [])
            )

        if enriched:
            doc.reference.update(enriched)
            print(f"✅ Updated {data.get('name')} with: {list(enriched.keys())}")
            time.sleep(0.2)  # Optional rate limiting
        else:
            print(f"⚠️  No enrichment data for {data.get('name')}.")

# ─── Entry Point ────────────────────────────────────────────
if __name__ == "__main__":
    enrich_all_venues("Los Angeles")
