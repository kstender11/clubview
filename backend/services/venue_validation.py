# services/venue_validation.py
import re
from datetime import time
from typing import Optional
from services.instagram import validate_instagram

# ───────────────────  CONSTANTS  ────────────────────
WHITELIST = {
    "the spare room",
    "dots space la",
    "plaza nightclub and dance hall",
    "the dime fairfax",
    "offshore beach house",
    "kings row gastropub",
    "el cid",
    "the edmon",
    "shrine room karaoke | la",
    "rocco’s weho",
    "poppy",
    "perch",
    "keys",
    "wolfsglen",
    "ōwa",
}


# ── add / extend keywords ──
POS_KW = {
    # single words
    "bar", "club", "lounge", "nightclub", "pub", "tavern",
    "karaoke", "speakeasy", "cantina", "saloon", "brewery",
    "taproom", "cocktail", "dive", "house", "agave",
    "tiki", "gastropub", "cerveceria", "karaoke",
    # phrases
    "beer garden", "wine bar", "dance hall", "beer hall"
}


NEG_KW_PLAIN = {
    "dispensary", "grocery", "supermarket", "liquor store",
    "pharmacy", "clinic", "hospital", "bank", "atm",
    "barber", "nail", "spa", "tanning", "market",
    "school", "academy", "daycare", "hardware", "laundromat",
    "dry cleaner"
}

BEAUTY_TERMS = {"beauty", "hair", "nail", "barber", "spa"}

GOOGLE_NIGHTLIFE_TYPES = {"bar", "night_club"}
THRESHOLD = 30  # ← main tuning knob

# ───────────────────  HELPERS  ────────────────────
def _count_kw(text: str) -> int:
    """Count how many POS_KW appear (word‑boundary for single words,
       substring for phrases)."""
    hits = 0
    for kw in POS_KW:
        if " " in kw:                           # phrase
            if kw in text:
                hits += 1
        else:                                   # single word
            if re.search(rf"\b{kw}\b", text):
                hits += 1
    return hits

def _is_beauty_salon(text: str) -> bool:
    return "salon" in text and any(word in text for word in BEAUTY_TERMS)

def _has_late_hours(hours: Optional[dict]) -> bool:
    """
    Returns True if venue ever closes 23:00‑06:00.

    Accepts these per‑day shapes:
      [('11:00', '02:00')]        # normal pair
      ['11:00-02:00']             # single string
      ['11:00', '02:00']          # orphaned 2‑item list
    Silently ignores malformed blocks.
    """
    if not hours:
        return False

    for blocks in hours.values():
        for block in blocks:
            # case 1: tuple/list pair
            if isinstance(block, (list, tuple)) and len(block) == 2:
                _, close_str = block
            # case 2: single 'open-close' string
            elif isinstance(block, str) and "-" in block:
                _, close_str = block.split("-", 1)
            else:
                continue  # unknown → skip

            try:
                close_t = time.fromisoformat(close_str)
            except ValueError:
                continue

            if close_t >= time(23, 0) or close_t < time(6, 0):
                return True
    return False

# ───────────────────  MAIN  ────────────────────
# services/venue_validation.py

def validate_venue(v: dict) -> bool:
    name   = v.get("name", "").lower()
    types  = [t.lower() for t in v.get("types", [])]
    cats   = [c.lower() for c in v.get("categories", [])]
    site   = v.get("website", "")
    hours  = v.get("hours")  # dict or None
    blob   = " ".join([name, *types, *cats])

    # 0. Whitelist wins
    if name in WHITELIST:
        return True

    # 1. Hard negative: if a bad keyword is present and NO nightlife cues
    if any(bad in blob for bad in NEG_KW_PLAIN) and _count_kw(blob) == 0:
        return False

    # 2. Beauty salon exclusion
    if _is_beauty_salon(blob):
        return False

    score = 0

    # 3. Foursquare "nightlife" flag
    if v.get("is_nightlife"):
        score += 40

    # 4. Google bar/night_club types
    if any(t in GOOGLE_NIGHTLIFE_TYPES for t in types):
        score += 25

    # 5. Name & category keywords
    name_hits = _count_kw(name)
    score += min(1, name_hits) * 20
    score += max(0, name_hits - 1) * 5
    score += _count_kw(" ".join(cats)) * 10

    # 6. Instagram bio presence
    if site and validate_instagram(site):
        score += 15

    # 7. Late night hours
    if _has_late_hours(hours):
        score += 10

    return score >= THRESHOLD
