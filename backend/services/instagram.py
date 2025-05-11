# instagram.py (new)
import requests
from core.config import get_settings

cfg = get_settings()

INSTAGRAM_KEYWORDS = {
    'bar', 'club', 'cocktails', 'nightlife', 'speakeasy',
    'draft', 'taproom', 'mixology', 'djs', 'dancing'
}

def validate_instagram(handle: str) -> bool:
    if not handle or not cfg.INSTAGRAM_TOKEN:
        return False
        
    try:
        url = f"https://graph.instagram.com/{handle}?fields=biography&access_token={cfg.INSTAGRAM_TOKEN}"
        response = requests.get(url, timeout=8).json()
        bio = response.get("biography", "").lower()
        return any(kw in bio for kw in INSTAGRAM_KEYWORDS)
    except Exception as e:
        print(f"Instagram validation error: {e}")
        return False