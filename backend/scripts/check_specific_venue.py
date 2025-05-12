#!/usr/bin/env python3
"""
scripts/check_specific_venue.py
Checks if a specific venue exists in Firestore.
"""

import firebase_admin
from firebase_admin import credentials, firestore, initialize_app

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)
db = firestore.client()

CITY = "Los Angeles"
TARGET_NAME = "house of meatballs"

def main():
    venues_ref = db.collection("cities").document(CITY).collection("venues")
    docs = venues_ref.stream()

    found = False
    for doc in docs:
        name = doc.to_dict().get("name", "").strip().lower()
        if TARGET_NAME == name:
            print(f"✅ Found: {doc.to_dict().get('name')} (doc ID: {doc.id})")
            found = True
            break

    if not found:
        print("❌ House of Meatballs not found in Firestore.")

if __name__ == "__main__":
    main()
