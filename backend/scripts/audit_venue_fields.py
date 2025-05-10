import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase app
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Fields to check for presence, including nested fields
REQUIRED_FIELDS = [
    "name", "address", "location.lat", "location.lng",
    "place_id", "foursquare_id",
    "categories", "types",
    "summary", "website", "instagram_url",
    "city", "state"
]

OPTIONAL_FIELDS = [
    "tips", "rating", "price_level", "popularity", "likes", "hours"
]

def has_nested_field(data, field_path):
    """Check if a nested field like 'location.lat' exists and has a value."""
    keys = field_path.split(".")
    for key in keys:
        if not isinstance(data, dict) or key not in data or data[key] in (None, "", []):
            return False
        data = data[key]
    return True

def audit_venues():
    print("\n📝 Starting audit of venue metadata...")
    venues_ref = db.collection("venues")
    docs = list(venues_ref.stream())
    print(f"📦 Found {len(docs)} venues.")

    for doc in docs:
        data = doc.to_dict()
        name = data.get("name", "Unknown")
        missing = [f for f in REQUIRED_FIELDS if not has_nested_field(data, f)]

        if missing:
            print(f"⚠️ {name} is missing: {', '.join(missing)}")
        else:
            print(f"✅ {name} has all required fields.")

if __name__ == "__main__":
    audit_venues()
