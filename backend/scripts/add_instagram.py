import requests
from bs4 import BeautifulSoup
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin

# Init Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    initialize_app(cred)

db = firestore.client()

def find_instagram_link(website_url):
    if not website_url:
        return None

    try:
        res = requests.get(website_url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "instagram.com" in href:
                return href.split("?")[0]  # Remove URL parameters
    except Exception as e:
        print(f"⚠️  Error fetching {website_url}: {e}")
    return None

def enrich_instagram():
    print("🔍 Starting Instagram enrichment...")
    venues_ref = db.collection("venues")
    docs = list(venues_ref.stream())
    print(f"📦 Found {len(docs)} venues.")

    for doc in docs:
        data = doc.to_dict()
        name = data.get("name")
        website = data.get("website")

        if not website:
            print(f"⏭️ Skipping {name} — no website.")
            continue

        instagram_url = data.get("instagram_url")
        if instagram_url:
            print(f"✅ {name} already has Instagram.")
            continue

        insta = find_instagram_link(website)
        if insta:
            doc.reference.update({"instagram_url": insta})
            print(f"📸 Updated {name} with Instagram: {insta}")
        else:
            print(f"❌ No Instagram found for {name}.")

if __name__ == "__main__":
    enrich_instagram()
