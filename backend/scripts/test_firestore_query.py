# scripts/test_firestore_query.py
from services.firestore_utils import db

def test_firestore_discover():
    query = db.collection("venues")\
              .where("city", "==", "Los Angeles")\
              .order_by("distance")\
              .limit(10)

    results = query.stream()
    for doc in results:
        data = doc.to_dict()
        print(f"{doc.id}: {data.get('name')} | city={data.get('city')} | distance={data.get('distance')}")

test_firestore_discover()
