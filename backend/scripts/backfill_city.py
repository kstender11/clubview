from services.firestore_utils import db

batch = db.batch()
for doc in db.collection("venues").stream():
    data = doc.to_dict()
    if data.get("city") is None:
        batch.update(doc.reference, {"city": "Los Angeles"})
batch.commit()
print("✅ City field backfilled for existing venues.")
