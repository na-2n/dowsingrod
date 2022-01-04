import requests

try:
    import ujson as json
except:
    import json

from furl import furl
from dataclasses import dataclass
from urllib.parse import urlencode
from typing import Optional, Collection, Sequence
from datetime import datetime


@dataclass
class Post:
    id: int
    created_at: float
    uploader_id: int
    score: int
    source: str
    md5: str
    #last_comment_bumped_at
    rating: str
    image_width: int
    image_height: int
    tags: list[str]
    #is_note_locked
    #fav_count
    file_ext: str
    #last_noted_at
    #is_rating_locked
    parent_id: int
    has_children: bool
    approver_id: int
    #tag_count_general
    #tag_count_artist
    #tag_count_character
    #tag_count_copyright
    file_size: int
    #is_status_locked
    #up_score
    #down_score
    #is_pending
    #is_flagged
    #is_deleted
    #tag_count
    #updated_at
    #is_banned


class Danbooru:
    BASE_URL = 'https://danbooru.donmai.us/'
    USER_AGENT = 'Dowsing Rod v0.1'

    def __init__(self, base_url=Danbooru.BASE_URL):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = self.USER_AGENT
        self.base_url = base_url

    def count_posts(self, tags: Sequence[str]):
        req = self._request('/counts/posts.json', tags=tags)

    def posts(self, tags: Sequence[str], page=1) -> List[Post]:
        req = self._request('/posts.json', tags=tags, page=page)

    def _request(self, endpoint: str, tags: Optional[Sequence[str]] = None, headers={}, **kwargs):
        if kwargs.get('tags'):
            kwargs['tags'] = self._build_tags(kwargs['tags'])

        req = self.session.get(self._build_url(endpoint, **kwargs))
        req.raise_for_status()

        return req

    def _build_url(self, endpoint: str, **kwargs):
        return furl(self.base_url, kwargs, endpoint).url

    def _build_tags(self, tags: Sequence[str]):
        return '+'.join(urlencode(x) for x in tags)

