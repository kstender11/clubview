import csv
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app

# ─── Firebase Setup ───────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)

db = firestore.client()

# ─── Full Export with All Fields ─────────────────────────────
def export_full_venues(city: str = "Los Angeles", output_file: str = "full_venues_export.csv"):
    venues_ref = db.collection("cities").document(city).collection("venues")
    docs = list(venues_ref.stream())

    print(f"📦 Exporting {len(docs)} venues to {output_file}...")

    # Full list of fields, with "name" forced to come first
    fields = [
        "name", "address", "categories", "category_ids", "city", "description", "distance",
        "foursquare_id", "hours", "instagram_url", "is_nightlife", "last_fsq_refresh",
        "lat", "lng", "place_id", "popularity", "price_level", "rating", "social_media",
        "state", "summary", "tips", "types", "website"
    ]

    with open(output_file, mode="w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for doc in docs:
            data = doc.to_dict()

            # Flatten fields for export
            row = {field: data.get(field, "") for field in fields}

            # Handle list fields
           # Handle list fields (convert each item to string first)
            if isinstance(row.get("categories"), list):
                row["categories"] = ", ".join(str(x) for x in row["categories"])
            if isinstance(row.get("category_ids"), list):
                row["category_ids"] = ", ".join(str(x) for x in row["category_ids"])
            if isinstance(row.get("types"), list):
                row["types"] = ", ".join(str(x) for x in row["types"])
            if isinstance(row.get("tips"), list):
                row["tips"] = " | ".join(str(x) for x in row["tips"])


            writer.writerow(row)

    print("✅ Export complete!")

# ─── Run Script ─────────────────────────────
if __name__ == "__main__":
    export_full_venues("Los Angeles")
