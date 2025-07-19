import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def migrate_menlo_park_to_flat():
    city_name = "Menlo Park"
    venues_ref = db.collection("cities").document(city_name).collection("venues")
    venues = venues_ref.stream()
    total = 0

    for venue in venues:
        data = venue.to_dict()
        if not data:
            continue

        data["city"] = city_name  # tag each document with its city
        db.collection("venues").document(venue.id).set(data)
        total += 1

    print(f"✅ Copied {total} venues from {city_name} into top-level 'venues/' collection.")

if __name__ == "__main__":
    migrate_menlo_park_to_flat()
