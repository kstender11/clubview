from services.venue_validation import validate_venue
import firebase_admin
from firebase_admin import credentials, firestore

# Setup Firestore
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

CITY = "Los Angeles"
ref = db.collection("cities").document(CITY).collection("venues")

deleted = 0
for doc in ref.stream():
    data = doc.to_dict()
    name = data.get("name", "").strip().lower()

    if not validate_venue(data):
        print(f"🗑 Deleting: {name}")
        doc.reference.delete()
        deleted += 1

print(f"\n✅ Deleted {deleted} venues from '{CITY}' collection.")
