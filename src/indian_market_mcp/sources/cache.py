from __future__ import annotations

import diskcache
import os
import hashlib
from typing import Any

CACHE_DIR = os.path.expanduser("~/.cache/indian-market-mcp")

_cache = diskcache.Cache(CACHE_DIR, size_limit=500 * 1024 * 1024)


def get(key: str) -> Any | None:
    return _cache.get(key)


def set(key: str, value: Any, ttl: int = 180) -> None:
    _cache.set(key, value, expire=ttl)


def make_key(*parts: str) -> str:
    raw = ":".join(str(p) for p in parts)
    return hashlib.md5(raw.encode()).hexdigest()


def cached(ttl: int = 180):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            key = make_key(func.__name__, *[str(a) for a in args], *[f"{k}={v}" for k, v in sorted(kwargs.items())])
            result = get(key)
            if result is not None:
                return result
            result = await func(*args, **kwargs)
            if result is not None:
                set(key, result, ttl)
            return result
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator
