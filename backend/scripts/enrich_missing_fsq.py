import time
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from core.config import get_settings
from services.foursquare import enrich_with_foursquare
from scripts.add_hours import get_google_hours
from scripts.add_fsq_ids import fetch_fsq_id
from services.instagram import find_instagram_link

cfg = get_settings()

# ─── Firebase Setup ─────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)

db = firestore.client()

# ─── Constants ─────────────────────────────
VENUE_NAMES = [
    "3 and Out Sports Bar & Lounge", "Not No Bar", "Lock & Key", "Lilly Rose", "Shorebar",
    "El Prado", "Tiny's", "Doheny Room", "Wawrwick LA", "Zebulon", "Dada Echo Park",
    "Bathtub Gin", "Harlowe Bar", "Eighty Two", "Checker Hall", "Circle Bar", "General Lee's",
    "The Virgil", "Honey's at Star Love", "Gran Blanco", "Keys night club", "The spotlight",
    "Offsunset", "Tenants of the Trees", "Gold Line", "Good Housekeeping", "Blind Barber",
    "Surly Goat", "Ballet", "Resident", "Lindens speakeasy",
    "Homage Brewing", "Apt 200", "The Friend Silverlake", "Jumbo's Clown Room", "Pangea Sound parties",
    "Lol Wine Bar", "El Chucho", "The Ruby Fruit", "The Varnish", "AKBar", "Club Baha",
    "Zouk Los Angeles", "Bar Flores"
]

CITY = "Los Angeles"

# ─── Main Enrichment ─────────────────────────────
def enrich_venue_data():
    venues_ref = db.collection("cities").document(CITY).collection("venues")

    for name in VENUE_NAMES:
        docs = list(venues_ref.where("name", "==", name).stream())
        if not docs:
            print(f"❌ Venue not found: {name}")
            continue

        doc = docs[0]
        data = doc.to_dict()
        updates = {}

        # Add Foursquare ID if missing
        if not data.get("foursquare_id"):
            loc = data.get("location", {})
            lat, lng = loc.get("lat"), loc.get("lng")
            fsq_id = fetch_fsq_id(name, lat, lng)
            if fsq_id:
                updates["foursquare_id"] = fsq_id
                print(f"   • Foursquare ID added for {name}: {fsq_id}")
            else:
                print(f"❌ Could not find Foursquare ID for {name}")

        # Enrich with Foursquare if ID exists
        fsq_id = updates.get("foursquare_id") or data.get("foursquare_id")
        if fsq_id:
            fsq_data = enrich_with_foursquare(fsq_id)
            if fsq_data:
                updates.update(fsq_data)
                print(f"   • Enriched Foursquare data for {name}")

        # Add hours if missing
        if not data.get("hours"):
            place_id = data.get("place_id")
            if place_id:
                hrs = get_google_hours(place_id)
                if hrs:
                    updates["hours"] = hrs
                    print(f"   • Hours added for {name}")

        # Add Instagram if missing
        if not data.get("instagram_url") and data.get("website"):
            insta = find_instagram_link(data.get("website"))
            if insta:
                updates["instagram_url"] = insta
                print(f"   • Instagram added for {name}")

        # Save to Firestore
        if updates:
            doc.reference.update(updates)
            print(f"✅ Updated {name} with: {list(updates.keys())}")
        else:
            print(f"⏭️  Skipped {name} — no updates needed.")

        time.sleep(0.2)

if __name__ == "__main__":
    enrich_venue_data()