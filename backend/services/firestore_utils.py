import firebase_admin
from firebase_admin import credentials, firestore
from core.config import get_settings
import os

cfg = get_settings()

# Initialize Firebase app only once
if not firebase_admin._apps:
    cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), "..", "firebase_key.json"))
    firebase_admin.initialize_app(cred)


db = firestore.client()

def add_venue_to_firestore(data: dict):
    # Use Google Place ID as document ID (globally unique)
    doc_ref = db.collection("venues").document(data["place_id"])
    doc_ref.set(data, merge=True)  # merge=True allows updating existing docs

