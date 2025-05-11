import os
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from core.config import get_settings

cfg = get_settings()

# 🔐 Firebase setup
key_path = os.path.abspath("firebase_key.json")
if not firebase_admin._apps:
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def fetch_fsq_id(name: str, lat: float, lng: float):
    url = "https://api.foursquare.com/v3/places/search"
    headers = {
        "Authorization": cfg.FOURSQUARE_API_KEY,
        "Accept": "application/json"
    }
    params = {
        "query": name,
        "ll": f"{lat},{lng}",
        "limit": 1
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        if response.status_code == 200:
            results = response.json().get("results")
            if results:
                return results[0]["fsq_id"]
    except Exception as e:
        print(f"🔴 Foursquare search error: {e}")
    return None

def add_missing_fsq_ids():
    print("🔍 Scanning venues...")
    venues_ref = db.collection("cities").document(city).collection("venues")
    docs = venues_ref.stream()

    for doc in docs:
        data = doc.to_dict()
        name = data.get("name")
        loc = data.get("location", {})

        if data.get("foursquare_id") or not name or not loc:
            continue

        lat, lng = loc.get("lat"), loc.get("lng")
        if not lat or not lng:
            print(f"❌ Missing coordinates for {name}")
            continue

        print(f"🔎 Searching Foursquare ID for: {name}")
        fsq_id = fetch_fsq_id(name, lat, lng)

        if fsq_id:
            doc.reference.update({"foursquare_id": fsq_id})
            print(f"✅ Added Foursquare ID to {name}: {fsq_id}")
        else:
            print(f"⚠️ No Foursquare match found for {name}")

    print("✅ Done assigning Foursquare IDs.")

if __name__ == "__main__":
    add_missing_fsq_ids()
