#!/usr/bin/env python3
"""
scripts/export_venues_to_csv.py
Export all validated venues from Firestore to a CSV file for manual review.
"""

import csv, firebase_admin
from firebase_admin import credentials, firestore, initialize_app

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)
db = firestore.client()

CITY = "San Francisco"
OUTPUT_CSV = "venues_export.csv"

def flatten_field(value):
    """Helper to stringify nested values for CSV."""
    if isinstance(value, dict):
        return str(value)
    elif isinstance(value, list):
        return ", ".join(str(x) for x in value)
    else:
        return value

def main():
    venues_ref = db.collection("cities").document(CITY).collection("venues")
    docs = list(venues_ref.stream())
    print(f"📦 Found {len(docs)} venues")

    # 🔍 Detect all fields used in Firestore
    fieldnames = set()
    for doc in docs:
        data = doc.to_dict()
        fieldnames.update(data.keys())
        if "location" in data:
            fieldnames.add("lat")
            fieldnames.add("lng")

    # Final set of CSV columns (remove 'location', sort)
    fieldnames = sorted(fieldnames - {"location"}) + ["lat", "lng"]
    print(f"📝 Writing {len(fieldnames)} columns to {OUTPUT_CSV}...")

    # ✍️ Write CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for doc in docs:
            data = doc.to_dict()

            # Flatten fields for CSV
            flat = {k: flatten_field(v) for k, v in data.items() if k != "location"}

            # Extract lat/lng if present
            if "location" in data:
                flat["lat"] = data["location"].get("lat")
                flat["lng"] = data["location"].get("lng")

            writer.writerow(flat)

    print("✅ Export complete.")

if __name__ == "__main__":
    main()
