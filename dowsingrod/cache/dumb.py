from typing import Any, Optional, Tuple, Dict
from time import time

from dowsingrod.cache.base import Cache


class DumbCache(Cache):
    def __init__(self):
        self._items: Dict[str, Tuple[Any, Optional[float]]]  = {}

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        item, ex_at = self._items.get(key, (default, None))

        if ex_at and time() > ex_at:
            del self._items[key]
            return default

        return item

    def set(self, key: str, value: Any, expire: Optional[int] = None):
        self._items[key] = value, time() + expire if expire else None

    def delete(self, key: str):
        del self._items[key]

