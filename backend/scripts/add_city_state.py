from firebase_admin import credentials, firestore, initialize_app
import firebase_admin

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)

db = firestore.client()

def update_city_state():
    venues_ref = db.collection("cities").document(city).collection("venues")
    docs = list(venues_ref.stream())

    for doc in docs:
        venue = doc.to_dict()
        lat = venue.get("location", {}).get("lat", 0)
        lng = venue.get("location", {}).get("lng", 0)

        if 33.5 < lat < 34.5 and -119 < lng < -117:
            city = "Los Angeles"
            state = "CA"
        elif 37.5 < lat < 38.5 and -123 < lng < -121:
            city = "San Francisco"
            state = "CA"
        else:
            city = "Unknown"
            state = "Unknown"

        doc.reference.update({
            "city": city,
            "state": state
        })
        print(f"✅ Updated {venue.get('name')} with city={city}, state={state}")

if __name__ == "__main__":
    update_city_state()
