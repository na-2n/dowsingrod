import requests

from abc import ABC
from typing import Any, Optional
from furl import furl


class ApiBase(ABC):
    USER_AGENT = "Dowsing Rod v0.1"

    def __init__(self, base_url: str, user_agent: Optional[str] = None):
        self._base_url = base_url
        self._session = requests.Session()
        self._session.headers['User-Agent'] = user_agent or self.USER_AGENT

    def _build_url(self, endpoint: str):
        f = furl(self._base_url)
        f.path.add(endpoint.lstrip('/'))

        return f.url

    def _request(self, endpoint: str, headers: dict[str, Any] = {}, error=True, **kwargs):
        req = self._session.get(self._build_url(endpoint), params=kwargs, headers=headers)

        if error:
            req.raise_for_status()

        return req

