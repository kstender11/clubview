
#!/usr/bin/env python3
"""
scripts/backfill_missing_venues.py
Search for missing known venues by name and insert them directly into Firestore (skip validation).
"""

import time, requests, firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from core.config import get_settings
from scripts.add_fsq_ids import fetch_fsq_id
from scripts.add_hours import get_google_hours
from scripts.add_instagram import find_instagram_link
from services.foursquare import enrich_with_foursquare

cfg = get_settings()

# ──────── Firebase ────────
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)
db = firestore.client()

# ──────── Google Places Text Search ────────
def search_google_place(name: str, location="34.0522,-118.2437", radius=25000):
    url = (
        "https://maps.googleapis.com/maps/api/place/textsearch/json"
        f"?query={requests.utils.quote(name)}"
        f"&location={location}&radius={radius}"
        f"&key={cfg.GOOGLE_KEY}"
    )
    res = requests.get(url, timeout=10).json()
    return res.get("results", [])[0] if res.get("results") else None

def get_google_details(place_id: str):
    url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&fields=website,editorial_summary"
        f"&key={cfg.GOOGLE_KEY}"
    )
    try:
        res = requests.get(url, timeout=10).json()
        r = res.get("result", {})
        return {
            "website": r.get("website"),
            "summary": r.get("editorial_summary", {}).get("overview")
        }
    except:
        return {}

# ──────── Backfill logic ────────
def backfill_venue(name: str, city: str = "Los Angeles"):
    print(f"🔍 Searching for '{name}'...")
    result = search_google_place(name)
    if not result:
        print(f"⚠️  No result found for {name}")
        return

    loc = result.get("geometry", {}).get("location", {})
    doc = {
        "name": result.get("name"),
        "address": result.get("formatted_address"),
        "place_id": result.get("place_id"),
        "rating": result.get("rating"),
        "price_level": result.get("price_level"),
        "types": result.get("types", []),
        "location": {"lat": loc.get("lat"), "lng": loc.get("lng")},
        "distance": 0,
        "foursquare_id": None,
        "categories": [],
        "summary": None,
        "website": None,
        "instagram_url": None,
        "hours": None,
        "city": city,
        "state": "CA",
    }

    ref = db.collection("cities").document(city).collection("venues").document(doc["place_id"])
    ref.set(doc)
    print(f"✅ Inserted {doc['name']}")

    # Enrich
    fsq = fetch_fsq_id(doc["name"], loc.get("lat"), loc.get("lng"))
    if fsq:
        ref.update({"foursquare_id": fsq})
        doc["foursquare_id"] = fsq
        print(f"   • added Foursquare ID {fsq}")

    if doc.get("foursquare_id"):
        enrich = enrich_with_foursquare(doc["foursquare_id"])
        if enrich:
            ref.update(enrich)
            print("   • enriched from Foursquare")

    patch = get_google_details(doc["place_id"])
    if patch:
        ref.update(patch)
        print("   • added website/summary from Google")

    hrs = get_google_hours(doc["place_id"])
    if hrs:
        ref.update({"hours": hrs})
        print("   • added hours")

    if doc.get("website"):
        insta = find_instagram_link(doc["website"])
        if insta:
            ref.update({"instagram_url": insta})
            print("   • added Instagram")

    time.sleep(0.3)

# ──────── List of known missing venues ────────
missing_venues = [
    "1212 santa monica", "33 taps dtla", "academy la", "apothéke la", "apt 503", "arena ktown", "arts district brewing", "avalon hollywood",
    "bacari west adams", "bamboo house", "bar lis", "bardot (at avalon)", "barney's beanery", "beer belly", "belles beach house", "biergarten la",
    "big dean's ocean front cafe", "boardner's", "break room 86", "brennan's", "broken shaker", "broxton brewery & pub", "burgundy room", "burlington room",
    "busby's west", "cabo cantina (hollywood)", "cabo cantina (santa monica)", "cafe brass monkey", "calabra (proper hotel)", "canary",
    "casa del mar (terrazza lounge)", "cat & fiddle", "chez jay", "clifton's republic", "dan sung sa", "desert 5 spot", "dirty laundry", "dragonfly hollywood",
    "dwit gol mok", "el chucho", "elbow room", "elephante beach house", "employees only la", "escala", "exchange la", "father's office", "firefly",
    "frank 'n hank", "frolic room", "gaam karaoke", "golden gopher", "good times at davey wayne's", "grandmaster recorders", "habibi café", "harriett's rooftop",
    "harvard & stone", "harvelle's", "hi tops", "hinano café", "hotel café", "hyde sunset", "intercrew", "jameson's pub", "juneshine", "keys nightclub",
    "kiss kiss bang bang", "la barca restaurant", "la chupería (“the miche spot”)", "la descarga", "la mesa", "laces", "lanea", "library alehouse",
    "living room bar at w hotel", "lock & key", "los globos", "madam siam", "mama lion", "melrose umbrella co.", "mother lode", "nalu vida venice", "neat",
    "nine o five (905 bar)", "no vacancy", "offhand wine bar", "palm tree karaoke", "paper tiger bar", "pare room", "perch", "ph day club",
    "pharaoh karaoke lounge", "poppy", "potions & poisons", "power house", "prank bar", "q's billiard club (adjacent)", "revolver", "rick's tavern on main",
    "rocco's tavern", "rocco's weho", "rock & reilly's usc village", "roosterfish", "rosen karaoke", "rustic canyon", "rusty's surf ranch",
    "santa monica brew works", "scum & villainy cantina", "seaside on the pier", "senator jones", "seven grand", "shorebar", "sidewalk café",
    "sinners y santos", "skylight gardens", "sonny mclean's", "soopsok karaoke", "sound", "southland beer", "station hollywood", "stk los angeles (westwood)",
    "sugar palm (viceroy)", "sunset at edition", "tavern", "te'kila", "terra cotta", "the abbey", "the belasco", "the bourbon room", "the brig", "the brixton",
    "the bungalow", "the coco club", "the continental club", "the craftsman bar & kitchen", "the daily pint", "the edison", "the galley", "the gaslite",
    "the georgian room", "the highlight room", "the hms bounty", "the lincoln", "the little friend bar", "the mayan", "the misfit", "the nickel mine",
    "the normandie club", "the otheroom", "the penthouse", "the prince", "the reserve", "the roof at edition", "the rooftop at the wayfarer",
    "the room hollywood", "the room santa monica", "the short stop", "the tuck room", "the venue", "the victorian", "the waterfront", "the wolves",
    "toe bang cafe", "townhouse & the del monte", "tramp stamp granny's", "trip", "venice beach bar", "venice whaler", "w hollywood - station 1640",
    "warwick", "west 4th & jane", "winston house", "wolfsglen", "ye olde king's head", "ōwa"
]


def main():
    for name in missing_venues:
        backfill_venue(name)

if __name__ == "__main__":
    main()
