from fastapi import APIRouter, Query
from typing import Optional
from services.firestore_utils import db
from services import google_places, foursquare, instagram
from services.cache import get_or_set

router = APIRouter()

@router.get("/venues/discover")
def discover_venues(
    city: str = "Los Angeles",
    category: Optional[str] = None,
    last_doc_id: Optional[str] = None,
    radius: int = 3000
):
    venues_ref = db.collection("venues")
    query = venues_ref.where("city", "==", city)

    if category:
        query = query.where("categories", "array_contains", category)

    query = query.order_by("distance").limit(20)

    if last_doc_id:
        last_doc = venues_ref.document(last_doc_id).get()
        if last_doc.exists:
            query = query.start_after(last_doc)

    results = query.stream()
    venues = [doc.to_dict() | {"id": doc.id} for doc in results]

    # Fallback: expand radius
    if len(venues) < 20 and radius < 8000:
        return discover_venues(city, category, last_doc_id, radius + 2000)

    # Fallback: drop radius if category filter is too strict
    if len(venues) < 20 and category:
        fallback_query = venues_ref.where("city", "==", city)\
                                   .where("categories", "array_contains", category)\
                                   .limit(20)
        fallback_results = fallback_query.stream()
        venues = [doc.to_dict() | {"id": doc.id} for doc in fallback_results]

    return venues
