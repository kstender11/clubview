import pytest
from services.venue_validation import validate_venue

@pytest.mark.parametrize("venue,expected", [
    # ✅ Should PASS
    ({"name": "ARARAT Restaurant Lounge Cafe", "types": ["bar"], "categories": ["Lounge"], "website": "", "hours": None}, True),
    ({"name": "Terrace Restaurant & Lounge", "types": ["bar"], "categories": ["Lounge"], "website": "", "hours": None}, True),
    ({"name": "Nineteen26 Bar & Lounge", "types": ["bar"], "categories": ["Bar"], "website": "", "hours": None}, True),
    ({"name": "Inkwell Tavern", "types": ["bar"], "categories": ["Tavern"], "website": "", "hours": None}, True),
    ({"name": "Broken Compass Tiki", "types": ["bar"], "categories": ["Tiki Bar"], "website": "", "hours": None}, True),
    ({"name": "Hilltop Restaurant and Bar", "types": ["bar"], "categories": ["Restaurant", "Bar"], "website": "", "hours": None}, True),
    ({"name": "Robin Hood British Pub", "types": ["bar"], "categories": ["Pub"], "website": "", "hours": None}, True),
    ({"name": "Spearmint Rhino Gentlemen's Club Van Nuys", "types": ["night_club"], "categories": ["Strip Club"], "website": "", "hours": None}, True),
    ({"name": "VLounge Bar And Night Club", "types": ["night_club"], "categories": ["Nightclub"], "website": "", "hours": None}, True),
    ({"name": "Carnival Karaoke", "types": ["bar"], "categories": ["Karaoke Bar"], "website": "", "hours": None}, True),

    # 🚫 Should FAIL
    ({"name": "Urban Press Winery & Restaurant", "types": ["restaurant"], "categories": ["Winery"], "website": "", "hours": None}, False),
    ({"name": "Bouvardia Venues", "types": [], "categories": [], "website": "", "hours": None}, False),
    ({"name": "Brewyard Beer Company", "types": ["restaurant"], "categories": ["Brewery"], "website": "", "hours": None}, False),
    ({"name": "The Green Room", "types": ["restaurant"], "categories": ["Fine Dining"], "website": "", "hours": None}, False),
    ({"name": "House of Meatballs", "types": ["restaurant"], "categories": ["Italian"], "website": "", "hours": None}, False),
    ({"name": "L'Orange Venues", "types": [], "categories": [], "website": "", "hours": None}, False),
    ({"name": "Round1 Bowling & Arcade", "types": ["amusement_center"], "categories": ["Arcade"], "website": "", "hours": None}, False),
    ({"name": "Copper Bucket", "types": ["restaurant"], "categories": [], "website": "", "hours": None}, False),
])
def test_validate_venue(venue, expected):
    assert validate_venue(venue) == expected
