try:
    import ujson as json
except:
    import json

from dataclasses import dataclass
from typing import Any, Optional, Sequence, List
from datetime import datetime

from dowsingrod.api_base import ApiBase


@dataclass
class Post:
    id: int
    created_at: datetime
    #uploader_id
    #score: int
    source: str
    #md5
    #last_comment_bumped_at
    rating: str
    image_width: int
    image_height: int
    #tag_string
    tags: List[str]
    #is_note_locked
    #fav_count
    file_ext: str
    #last_noted_at
    #is_rating_locked
    #parent_id
    #has_children
    #approver_id
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
    pixiv_id: Optional[int]
    #last_commented_at
    #has_active_children
    #bit_flags
    #tag_count_meta
    #has_large
    #has_visible_children
    #tag_string_general
    #tag_string_character
    character_tags: List[str]
    #tag_string_copyright
    #tag_string_artist
    #tag_string_meta
    file_url: str
    large_file_url: str
    preview_file_url: str


class DanbooruApi(ApiBase):
    BASE_URL = 'https://danbooru.donmai.us/'

    def __init__(self, base_url: Optional[str] = None):
        super().__init__(base_url or self.BASE_URL)

    def count_posts(self, tags: Sequence[str]) -> int:
        req = self._request('/counts/posts.json', tags=tags)
        obj = json.loads(req.text)

        return obj['counts']['posts']

    def posts(self, tags: Sequence[str], page=1) -> List[Post]:
        req = self._request('/posts.json', tags=tags, page=page)
        obj = json.loads(req.text)

        posts = []

        for post in filter(lambda x: x.get('file_url') is not None, obj):
            try:
                posts.append(Post(post.get('id', -1),
                    datetime.fromisoformat(post['created_at']),
                    post['source'],
                    post['rating'],
                    post['image_width'],
                    post['image_height'],
                    post['tag_string'].split(' '),
                    post['file_ext'],
                    post['file_size'],
                    post.get('pixiv_id'),
                    post['tag_string_character'].split(' '),
                    post['file_url'],
                    post['large_file_url'],
                    post['preview_file_url']))
            except:
                print('Error in post:')
                print(post)

        return posts

    def _request(self, endpoint: str, tags: Optional[Sequence[str]] = None, headers: dict[str, Any] = {}, **kwargs):
        if tags is not None:
            kwargs['tags'] = ' '.join(tags)

        return super()._request(endpoint, headers, **kwargs)

