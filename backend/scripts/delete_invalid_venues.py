#!/usr/bin/env python3
"""
scripts/delete_invalid_venues.py
Deletes venues in Firestore that fail nightlife validation.
"""

import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from services.venue_validation import validate_venue

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)
db = firestore.client()

CITY = "Los Angeles"

def main():
    venues_ref = db.collection("cities").document(CITY).collection("venues")
    docs = list(venues_ref.stream())

    print(f"\n🔍 Checking {len(docs)} venues for deletion...\n")
    to_delete = []

    for doc in docs:
        data = doc.to_dict()
        name = data.get("name", "UNKNOWN")
        if not validate_venue(data):
            to_delete.append((doc.id, name))

    if to_delete:
        print(f"⚠️  {len(to_delete)} invalid venues will be deleted:\n")
        for doc_id, name in sorted(to_delete, key=lambda x: x[1]):
            print(f"  - {name}")
            venues_ref.document(doc_id).delete()
        print("\n✅ Deletion complete.")
    else:
        print("✅ All venues passed validation. No deletions needed.")

if __name__ == "__main__":
    main()
