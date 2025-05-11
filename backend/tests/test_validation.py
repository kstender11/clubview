import sys
import os
import pytest

# Ensure backend root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.venue_validation import validate_venue

# --- Passing Cases ---

def test_basic_nightclub():
    venue = {
        "name": "Nightclub XYZ",
        "types": ["night_club"],
        "categories": ["Nightclub"],
        "is_nightlife": True
    }
    assert validate_venue(venue) is True

def test_instagram_validation(monkeypatch):
    monkeypatch.setattr("services.instagram.validate_instagram", lambda x: True)
    venue = {
        "name": "Secret Lounge",
        "website": "https://instagram.com/secret_bar",
        "types": ["point_of_interest", "bar"],  # this helps pass the score threshold
        "categories": []
    }
    assert validate_venue(venue) is True


def test_foursquare_only():
    venue = {
        "name": "Hidden Bar",
        "is_nightlife": True,
        "types": [],
        "categories": ["Bar"]
    }
    assert validate_venue(venue) is True

def test_fallback_with_multiple_keywords():
    venue = {
        "name": "The Speakeasy Club",
        "types": ["point_of_interest"],
        "categories": ["Cocktail Bar"]
    }
    assert validate_venue(venue) is True

# --- Failing Cases ---

def test_hard_exclude_dispensary():
    venue = {
        "name": "Green Cross",
        "types": ["store"],
        "categories": ["Dispensary"]
    }
    assert validate_venue(venue) is False

def test_hard_exclude_bodega():
    venue = {
        "name": "Bar Bodega",
        "types": ["store"],
        "categories": ["Bodega"]
    }
    assert validate_venue(venue) is False

def test_restaurant_with_bar_in_name():
    venue = {
        "name": "Pasta Bar",
        "types": ["restaurant"],
        "categories": ["Italian Restaurant"]
    }
    assert validate_venue(venue) is False

def test_single_keyword_not_enough():
    venue = {
        "name": "The Lounge",
        "types": ["point_of_interest"],
        "categories": []
    }
    assert validate_venue(venue) is False

def test_empty_data():
    venue = {}
    assert validate_venue(venue) is False

def test_nightlife_keyword_in_category_only():
    venue = {
        "name": "Random Place",
        "types": ["point_of_interest"],
        "categories": ["Club"]
    }
    assert validate_venue(venue) is False
