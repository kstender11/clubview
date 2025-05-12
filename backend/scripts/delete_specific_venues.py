#!/usr/bin/env python3
"""
scripts/delete_specific_venues.py
Delete a hardcoded list of specific venue names from Firestore (Los Angeles collection).
"""

import firebase_admin
from firebase_admin import credentials, firestore, initialize_app

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)
db = firestore.client()

CITY = "Los Angeles"
VENUES_TO_DELETE = [
    "Fleming’s Prime Steakhouse & Wine Bar",  # ← curly apostrophe
    "Yard House",
]


def delete_venue_by_name(name):
    venues_ref = db.collection("cities").document(CITY).collection("venues")
    docs = venues_ref.where("name", "==", name).stream()
    found = False
    for doc in docs:
        doc.reference.delete()
        print(f"🗑️ Deleted '{name}' (ID: {doc.id})")
        found = True
    if not found:
        print(f"⚠️ Venue not found: {name}")

def main():
    print(f"🔎 Attempting to delete {len(VENUES_TO_DELETE)} venues from {CITY}...")
    for name in VENUES_TO_DELETE:
        delete_venue_by_name(name)

if __name__ == "__main__":
    main()
