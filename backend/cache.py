import json
import time
import fnmatch
import redis
from flask import current_app

_client = None
_mode = "init"
_stats = {"hits": 0, "misses": 0, "sets": 0, "invalidations": 0}


class LocalCacheStore:
    def __init__(self):
        self.data = {}

    def get(self, key):
        entry = self.data.get(key)
        if not entry:
            return None
        val, exp = entry
        if exp and time.time() > exp:
            self.data.pop(key, None)
            return None
        return val

    def set(self, key, val, ex=None):
        exp = (time.time() + float(ex)) if ex else None
        self.data[key] = (val, exp)
        return True

    def keys(self, pattern="*"):
        now = time.time()
        out = []
        for k, (_, exp) in list(self.data.items()):
            if exp and now > exp:
                self.data.pop(k, None)
            elif fnmatch.fnmatch(k, pattern):
                out.append(k)
        return out

    def delete(self, *keys):
        count = 0
        for k in keys:
            if k in self.data:
                del self.data[k]
                count += 1
        return count

    def flushdb(self):
        self.data.clear()
        return True


def get_redis_client():
    global _client, _mode
    if _client is not None:
        return _client

    url = "redis://localhost:6379/0"
    try:
        if current_app:
            url = current_app.config.get("REDIS_URL", url)
    except RuntimeError:
        pass

    try:
        r = redis.Redis.from_url(url, decode_responses=True, socket_connect_timeout=0.5)
        r.ping()
        _client = r
        _mode = "redis"
    except Exception:
        _client = LocalCacheStore()
        _mode = "memory"

    return _client


def cache_get(key):
    c = get_redis_client()
    try:
        raw = c.get(key)
        if raw is not None:
            _stats["hits"] += 1
            return json.loads(raw)
        _stats["misses"] += 1
        return None
    except Exception:
        _stats["misses"] += 1
        return None


def cache_set(key, value, timeout=None):
    c = get_redis_client()
    if timeout is None:
        try:
            timeout = current_app.config.get("CACHE_DEFAULT_TIMEOUT", 120)
        except RuntimeError:
            timeout = 120
    try:
        c.set(key, json.dumps(value, default=str), ex=timeout)
        _stats["sets"] += 1
    except Exception:
        pass


def cache_invalidate_prefix(*prefixes):
    c = get_redis_client()
    try:
        for p in prefixes:
            matched = c.keys(f"{p}*")
            if matched:
                c.delete(*matched)
                _stats["invalidations"] += len(matched)
