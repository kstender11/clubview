import time
from threading import Lock
from collections import defaultdict

WINDOW = 60  # seconds
CALL_LIMIT = 90  # calls per window (leave headroom)

_lock = Lock()
_calls = defaultdict(list)

def is_allowed(api_name: str) -> bool:
    now = time.time()
    with _lock:
        _calls[api_name] = [t for t in _calls[api_name] if now - t < WINDOW]
        if len(_calls[api_name]) < CALL_LIMIT:
            _calls[api_name].append(now)
            return True
    return False
