import requests
import time
import firebase_admin
from bs4 import BeautifulSoup
from firebase_admin import credentials, firestore, initialize_app
from core.config import get_settings

cfg = get_settings()

# ─── Firebase Setup ───────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)

db = firestore.client()

# ─── Instagram Scraper ─────────────────────────────
def find_instagram_link(website_url):
    if not website_url:
        return None
    try:
        res = requests.get(website_url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "instagram.com" in href:
                return href.split("?")[0]
    except Exception as e:
        print(f"⚠️ Error fetching {website_url}: {e}")
    return None

# ─── Google Place Search + Details ────────────────
def search_google_place_id(name, city):
    query = f"{name}, {city}"
    url = (
        f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        f"?input={requests.utils.quote(query)}&inputtype=textquery&fields=place_id"
        f"&key={cfg.GOOGLE_KEY}"
    )
    try:
        res = requests.get(url, timeout=6).json()
        candidates = res.get("candidates")
        if candidates:
            return candidates[0].get("place_id")
    except Exception as e:
        print(f"❌ Google Place search error for {name}: {e}")
    return None

def get_google_details(place_id):
    url = (
        f"https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&fields=formatted_address,geometry,types,website,rating,price_level,name"
        f"&key={cfg.GOOGLE_KEY}"
    )
    try:
        res = requests.get(url, timeout=6).json()
        result = res.get("result", {})
        return {
            "address": result.get("formatted_address"),
            "lat": result.get("geometry", {}).get("location", {}).get("lat"),
            "lng": result.get("geometry", {}).get("location", {}).get("lng"),
            "types": result.get("types"),
            "website": result.get("website"),
            "rating": result.get("rating"),
            "price_level": result.get("price_level"),
            "place_id": place_id
        }
    except Exception as e:
        print(f"❌ Google Details error for {place_id}: {e}")
        return {}

# ─── Enrichment Runner ─────────────────────────────
def enrich_google_fields(city="Los Angeles"):
    print(f"🔍 Enriching venues in {city}...")
    venues_ref = db.collection("cities").document(city).collection("venues")
    docs = list(venues_ref.stream())

    for doc in docs:
        data = doc.to_dict()
        name = data.get("name")
        if not name:
            continue

        needs_enrich = any(
            not data.get(f) for f in ["address", "lat", "lng", "types", "place_id", "rating"]
        )

        if not needs_enrich:
            print(f"✅ {name} already enriched.")
            continue

        # 🔍 Find place_id if missing
        place_id = data.get("place_id") or search_google_place_id(name, city)
        if not place_id:
            print(f"❌ Skipping {name} — no Google match.")
            continue

        # 🌐 Fetch Google Place details
        details = get_google_details(place_id)
        if details:
            doc.reference.update(details)
            print(f"📍 Updated {name} with Google fields.")

        # 📸 Enrich Instagram if missing
        if not data.get("instagram_url") and details.get("website"):
            insta = find_instagram_link(details["website"])
            if insta:
                doc.reference.update({"instagram_url": insta})
                print(f"📸 Added Instagram for {name} → {insta}")

        time.sleep(0.2)  # Optional rate limit

# ─── Entry Point ─────────────────────────────
if __name__ == "__main__":
    enrich_google_fields("Los Angeles")