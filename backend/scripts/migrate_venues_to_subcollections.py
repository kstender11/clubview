from firebase_admin import credentials, firestore, initialize_app

# Initialize Firebase
cred = credentials.Certificate("firebase_key.json")
initialize_app(cred)
db = firestore.client()

def migrate_venues():
    top_level_ref = db.collection("venues")
    docs = top_level_ref.stream()
    migrated = 0

    for doc in docs:
        data = doc.to_dict()
        city = data.get("city", "Unknown")

        new_ref = db.collection("cities").document(city).collection("venues").document(doc.id)
        new_ref.set(data, merge=True)
        top_level_ref.document(doc.id).delete()
        migrated += 1
        print(f"✅ Migrated: {doc.id} → cities/{city}/venues/{doc.id}")

    print(f"\n🎉 Migration complete. {migrated} venues moved.")

if __name__ == "__main__":
    migrate_venues()
