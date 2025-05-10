import requests
from core.config import get_settings
from firebase_admin import credentials, firestore, initialize_app
from services.foursquare import enrich_with_foursquare
from typing import Optional
import firebase_admin

cfg = get_settings()

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)

db = firestore.client()

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
        print(f"Google details error: {e}")
        return {}

def generate_fallback_summary(categories):
    if categories:
        if len(categories) == 1:
            return f"A {categories[0]} in downtown LA."
        elif len(categories) == 2:
            return f"A {categories[0]} and {categories[1]} in downtown LA."
        else:
            return f"A {categories[0]}, {categories[1]}, and more in downtown LA."
    return None

def enrich_all_venues():
    print("🔍 Script started...")
    venues_ref = db.collection("venues")
    docs = list(venues_ref.stream())
    print(f"📦 Found {len(docs)} venues.")

    for doc in docs:
        data = doc.to_dict()
        fsq_id = data.get("foursquare_id")
        if not fsq_id:
            print(f"🚫 Skipping {data.get('name')} — no Foursquare ID.")
            continue

        enriched = enrich_with_foursquare(fsq_id)

        # Try Google website + editorial summary if not present from Foursquare
        if data.get("place_id"):
            google_data = get_google_website_and_summary(data["place_id"])
            if not enriched.get("website") and google_data.get("website"):
                enriched["website"] = google_data["website"]
            if not enriched.get("summary") and google_data.get("summary"):
                enriched["summary"] = google_data["summary"]

        # Fallback summary using categories
        if not enriched.get("summary"):
            enriched["summary"] = generate_fallback_summary(enriched.get("categories", []))

        if enriched:
            doc.reference.update(enriched)
            print(f"✅ Updated {data.get('name')} with: {enriched}")
        else:
            print(f"⚠️  No enrichment data for {data.get('name')}.")

if __name__ == "__main__":
    enrich_all_venues()
