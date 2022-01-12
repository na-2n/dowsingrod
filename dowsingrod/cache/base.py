from typing import Any, Optional
from abc import ABC, abstractmethod


class Cache(ABC):
    @abstractmethod
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        pass

    @abstractmethod
    def set(self, key: str, val: Any, expire: Optional[int] = None):
        pass

    @abstractmethod
    def delete(self, key: str):
        pass

    def __getitem__(self, name: str) -> Any:
        return self.get(name)

    def __setitem__(self, name: str, value: Any):
        return self.set(name, value)

    def __delitem__(self, name: str):
        return self.delete(name)

