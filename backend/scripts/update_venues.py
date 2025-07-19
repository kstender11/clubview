#!/usr/bin/env python3

import firebase_admin
from firebase_admin import credentials, firestore, initialize_app

# Initialize Firestore
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)
db = firestore.client()

CITY = "Los Angeles"

# ✅ Venues to ADD (manually curated)
VENUES_TO_ADD = [
    "Keys night club", "Not No Bar", "Ballet", "Tiny's", "El Chucho",
    "Bathtub Gin", "Lilly Rose", "The Varnish", "Lock & Key", "Blind Barber",
    "The Friend Silverlake", "Lindens speakeasy", "The spotlight", "Gran Blanco",
    "Harlowe Bar", "Surly Goat", "Gold Line", "Good Housekeeping", "Tenants of the Trees",
    "Bar Stella", "The Ruby Fruit", "Circle Bar", "Jumbo's Clown Room", "Lol Wine Bar",
    "Eighty Two", "Resident", "Bar Flores", "El Prado", "Pangea Sound parties",
    "Wawrwick LA", "Doheny Room", "Offsunset", "Zouk Los Angeles", "Shorebar",
    "Zebulon", "Checker Hall", "Apt 200", "General Lee's", "Homage Brewing",
    "Honey's at Star Love", "The Virgil", "Club Baha", "Dada Echo Park", "AKBar"
]

# ❌ Venues to DELETE
VENUES_TO_DELETE = [
    "Kava Bar LA & Botanical Lounge", "DeBell Golf Club",
    "Los Angeles Club Crawl", "Keys", "Shore Bar"
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

def add_placeholder_venue(name):
    venues_ref = db.collection("cities").document(CITY).collection("venues")
    existing = list(venues_ref.where("name", "==", name).stream())
    if existing:
        print(f"↪️ Already exists: {name}")
        return
    placeholder = {
        "name": name,
        "location": {"lat": None, "lng": None},
        "categories": ["bar", "nightlife"],
        "summary": "Manually added pending enrichment",
    }
    venues_ref.add(placeholder)
    print(f"Added placeholder: {name}")

def main():
    print("🧹 Deleting invalid venues...")
    for name in VENUES_TO_DELETE:
        delete_venue_by_name(name)

    print("\n📥 Adding missing venues...")
    for name in VENUES_TO_ADD:
        add_placeholder_venue(name)

if __name__ == "__main__":
    main()
