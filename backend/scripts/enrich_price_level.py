import firebase_admin
import requests
from firebase_admin import credentials, firestore, initialize_app
from core.config import get_settings

cfg = get_settings()

# ─── Firebase Setup ─────────────────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)

db = firestore.client()

# ─── Google Price Level Fetch ───────────────────────────────
def fetch_price_level(place_id: str) -> int:
    url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&fields=price_level"
        f"&key={cfg.GOOGLE_KEY}"
    )
    try:
        res = requests.get(url, timeout=5).json()
        return res.get("result", {}).get("price_level")
    except Exception as e:
        print(f"❌ Error fetching price level for {place_id}: {e}")
        return None

# ─── Patch Price Level for Missing Venues ───────────────────
def enrich_missing_price_levels(city: str = "Los Angeles"):
    venues_ref = db.collection("cities").document(city).collection("venues")
    docs = list(venues_ref.stream())
    print(f"🔍 Scanning {len(docs)} venues in {city} for missing price level...")

    updated = 0
    skipped = 0

    for doc in docs:
        data = doc.to_dict()
        place_id = data.get("place_id")
        price_level = data.get("price_level")

        if "price_level" in data and price_level is not None:
            skipped += 1
            continue  # Already has a value

        if not place_id:
            print(f"⚠️  Skipping {data.get('name')} — no place_id.")
            continue

        print(f"🔎 {data.get('name')}: place_id={place_id}, existing price_level={price_level}")

        fetched = fetch_price_level(place_id)
        print(f"   → Google returned price_level: {fetched}")

        if fetched is not None:
            doc.reference.update({"price_level": fetched})
            print(f"✅ Updated {data.get('name')} with price_level: {fetched}")
            updated += 1

    print(f"\n🏁 Done. Updated {updated} venues with price_level. Skipped {skipped} already-filled.")

# ─── Entry Point ────────────────────────────────────────────
if __name__ == "__main__":
    enrich_missing_price_levels("Los Angeles")
