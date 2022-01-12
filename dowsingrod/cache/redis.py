from typing import Any, Optional
from redis import Redis

from dowsingrod.cache.base import Cache


class RedisCache(Cache):
    def __init__(self, url: Optional[str] = None, *args, **kwargs):
        if url:
            self._redis = Redis.from_url(url, **kwargs)
        else:
            self._redis = Redis(*args, **kwargs)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self._redis.get(key) or default

    def set(self, key: str, value: Any, expire: Optional[int] = None):
        self._redis.set(key, value, ex=expire)

    def delete(self, key: str):
        self._redis.delete(key)

