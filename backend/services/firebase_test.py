from services.foursquare import enrich_with_foursquare

def upload_venues_to_firebase(lat: float, lng: float):
    venues = get_google_venues(lat, lng)
    for venue in venues:
        fsq_id = venue.get("foursquare_id")
        if fsq_id:
            enrichment = enrich_with_foursquare(fsq_id)
            venue.update(enrichment)
        simplified = simplify_venue(venue)
        add_venue_to_firestore(simplified)
