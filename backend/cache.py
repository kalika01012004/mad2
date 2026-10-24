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
