"""
A small in-memory TTL cache helper using cachetools.
Used for simple caching of analytics results. Replace with Redis-based cache for multi-process deployments.
"""
from cachetools import TTLCache

# default cache: 100 items, 300s TTL
cache = TTLCache(maxsize=100, ttl=300)

def cache_get(key):
    return cache.get(key)

def cache_set(key, value):
    cache[key] = value

def cache_clear():
    cache.clear()