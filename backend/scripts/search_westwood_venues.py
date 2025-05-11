# scripts/search_westwood_venues.py
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firestore
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Westwood coordinates
LAT_MIN, LAT_MAX = 34.05, 34.07
LNG_MIN, LNG_MAX = -118.45, -118.43

print("🔍 Searching for venues in Westwood area...\n")

venues_ref = db.collection("cities").document("Los Angeles").collection("venues")
results = []

for doc in venues_ref.stream():
    data = doc.to_dict()
    loc = data.get("location", {})
    lat, lng = loc.get("lat"), loc.get("lng")

    if lat and lng and LAT_MIN <= lat <= LAT_MAX and LNG_MIN <= lng <= LNG_MAX:
        results.append((data.get("name", "Unnamed"), lat, lng))

# Show results
if results:
    for name, lat, lng in results:
        print(f"✅ {name} ({lat}, {lng})")
else:
    print("❌ No venues found in Westwood.")
