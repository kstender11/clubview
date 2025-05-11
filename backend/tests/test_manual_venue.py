def test_scoring_logic(monkeypatch):
    # Mock Instagram
    monkeypatch.setattr("services.instagram.validate_instagram", lambda x: x == "https://instagram.com/secret_bar")

    test_cases = [
        # Should fail: restaurant
        ({"name": "Monkey King", "types": ["restaurant"], "categories": ["Asian Fusion"]}, False),

        # Should pass: clear club
        ({"name": "La Descarga", "types": ["night_club"], "categories": ["Nightclub"], "is_nightlife": True}, True),

        # Should fail: event space
        ({"name": "Cocktail Academy", "types": ["studio"], "categories": ["Mixology School"]}, False),

        # Should pass due to Instagram signal
        ({"name": "Secret Speakeasy", "types": ["point_of_interest"], "website": "https://instagram.com/secret_bar"}, True),
    ]

    for venue, expected in test_cases:
        assert validate_venue(venue, debug=True) == expected
