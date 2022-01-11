try:
    import ujson as json
except:
    import json

from typing import Any, Dict
from dataclasses import dataclass
from dowsingrod.api_base import ApiBase


class PixivEmbedError(Exception):
    pass


class PixivNotFoundError(PixivEmbedError):
    pass


@dataclass
class PixivArtworkEmbed:
    id: str
    title: str
    author_id: str
    author_name: str


class PixivEmbedApi(ApiBase):
    BASE_URL = "https://embed.pixiv.net/"

    def __init__(self):
        super().__init__(self.BASE_URL)

    def get_artwork(self, art_id: str) -> PixivArtworkEmbed:
        obj = self._query_url(f'https://www.pixiv.net/artworks/{art_id}')

        author_id = obj['author_url'].split('/')[-1]

        return PixivArtworkEmbed(art_id, obj['title'], author_id, obj['author_name'])


    def _query_url(self, url: str) -> Dict[str, Any]:
        req = self._request('/oembed.php', url=url, error=False)

        if req.status_code == 404:
            raise PixivNotFoundError()

        obj = json.loads(req.text)
        if not obj:
            raise PixivEmbedError("Pixiv returned an empty object, is your URL valid?")

        return obj

