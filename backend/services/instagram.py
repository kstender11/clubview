import requests
from core.config import get_settings
from bs4 import BeautifulSoup

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

# ✅ This is now properly placed at the module level
def find_instagram_link(website_url):
    if not website_url:
        return None
    try:
        res = requests.get(website_url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "instagram.com" in href:
                return href.split("?")[0]
    except Exception as e:
        print(f"⚠️  Error fetching {website_url}: {e}")
    return None
