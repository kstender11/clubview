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

CITY = "Los Angeles"
OUTPUT_CSV = "venues_export.csv"

def main():
    venues_ref = db.collection("cities").document(CITY).collection("venues")
    docs = list(venues_ref.stream())
    print(f"📦 Exporting {len(docs)} venues to {OUTPUT_CSV}")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name", "Address", "Categories", "Types", "Website",
            "Instagram", "Summary", "Hours", "Latitude", "Longitude"
        ])

        for doc in docs:
            data = doc.to_dict()
            loc = data.get("location", {})
            writer.writerow([
                data.get("name", ""),
                data.get("address", ""),
                ", ".join(data.get("categories", [])),
                ", ".join(data.get("types", [])),
                data.get("website", ""),
                data.get("instagram_url", ""),
                data.get("summary", ""),
                str(data.get("hours", "")),
                loc.get("lat", ""),
                loc.get("lng", "")
            ])

    print("✅ Export complete.")

if __name__ == "__main__":
    main()
