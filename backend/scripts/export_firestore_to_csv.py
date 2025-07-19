#!/usr/bin/env python3
"""
Export all venues from Firestore 'venues' collection to a CSV file.
Nested fields (like categories) are flattened.
"""

import csv
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")  # Update this if your file has a different name
    firebase_admin.initialize_app(cred)

db = firestore.client()
OUTPUT_CSV = "venues_export.csv"

def flatten_venue(venue_dict):
    flat = {}
    for key, value in venue_dict.items():
        if isinstance(value, list):
            flat[key] = ", ".join(str(item) for item in value)
        else:
            flat[key] = value
    return flat

def export_venues():
    print(f"📤 Exporting all documents from 'venues' → {OUTPUT_CSV}")
    venues_ref = db.collection("venues")
    docs = venues_ref.stream()

    data = []
    for doc in docs:
        venue = doc.to_dict()
        venue["id"] = doc.id  # Add document ID for reference
        flat_venue = flatten_venue(venue)
        data.append(flat_venue)

    if not data:
        print("⚠️ No venue data found.")
        return

    fieldnames = sorted({key for row in data for key in row})
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Exported {len(data)} venues to '{OUTPUT_CSV}'.")

if __name__ == "__main__":
    export_venues()
