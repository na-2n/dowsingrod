import sys

try:
    import ujson as json
except:
    import json

from dataclasses import asdict, is_dataclass
from typing import Any, Optional
from redis import Redis

from dowsingrod.cache.base import Cache


class RedisCache(Cache):
    def __init__(self, url: Optional[str] = None, *args, **kwargs):
        if url:
            self._redis = Redis.from_url(url, **kwargs)
        else:
            self._redis = Redis(*args, **kwargs)

    # holy fuck this is cancerous
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        val = self._redis.get(key)
        if not val:
            return default

        obj = json.loads(val)

        modname, tname = obj['_python_type'].rsplit('.', 1)
        data = obj['_data']

        if modname not in sys.modules:
            __import__(modname)

        mod = sys.modules[modname]
        t = getattr(mod, tname)

        if isinstance(data, dict):
            return t(**data)
        elif t is not list and isinstance(data, list) :
            return t(*data)
        else:
            return t(data)

    def set(self, key: str, value: Any, expire: Optional[int] = None):
        t = type(value)
        obj = {
            '_python_type': t.__module__ + '.' + t.__name__,
            '_data': asdict(value) if is_dataclass(value) else value
        }

        self._redis.set(key, json.dumps(obj), ex=expire)

    def delete(self, key: str):
        self._redis.delete(key)

