import requests
from core.config import get_settings
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin
import time

cfg = get_settings()

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)

db = firestore.client()

def get_google_hours(place_id):
    url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&fields=opening_hours"
        f"&key={cfg.GOOGLE_KEY}"
    )
    try:
        res = requests.get(url, timeout=5)
        result = res.json().get("result", {})
        weekday_text = result.get("opening_hours", {}).get("weekday_text")
        if weekday_text:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            return {
                day.lower(): text.split(": ", 1)[1]
                for day, text in zip(days, weekday_text)
            }
    except Exception as e:
        print(f"Google hours error for {place_id}: {e}")
    return None

def add_hours_to_venues():
    print("\n🕒 Starting hours enrichment...")
    venues_ref = db.collection("venues")
    docs = list(venues_ref.stream())
    print(f"📦 Found {len(docs)} venues.")

    for doc in docs:
        data = doc.to_dict()
        place_id = data.get("place_id")
        if not place_id:
            print(f"⏭️ Skipping {data.get('name')} — no place_id.")
            continue

        hours = get_google_hours(place_id)
        if hours:
            doc.reference.update({
                "hours": hours,
                "hours_note": firestore.DELETE_FIELD  # clear any old note
            })
            print(f"✅ Updated {data.get('name')} with hours.")
        else:
            doc.reference.update({
                "hours_note": "See website for hours"
            })
            print(f"❌ No hours found for {data.get('name')} — added fallback note.")
        time.sleep(0.1)  # rate limit safety

if __name__ == "__main__":
    add_hours_to_venues()
