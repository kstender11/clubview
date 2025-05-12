import json, redis, hashlib

rds = redis.Redis(host="localhost", port=6379, decode_responses=True)

def _key(name: str, params: dict) -> str:
    h = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
    return f"{name}:{h}"

def get_or_set(name: str, params: dict, ttl_hours: int, loader):
    k = _key(name, params)
    data = rds.get(k)
    if data:
        print(f"[CACHE HIT] {k}")
        return json.loads(data)
    print(f"[CACHE MISS] {k}")
    value = loader()
    rds.set(k, json.dumps(value), ex=ttl_hours * 3600)
    return value