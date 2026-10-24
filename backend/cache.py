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
