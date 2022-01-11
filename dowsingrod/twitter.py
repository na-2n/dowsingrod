try:
    import ujson as json
except:
    import json

from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence

from dowsingrod.api_base import ApiBase


class TwitterError(Exception):
    pass


class TwitterApiError(TwitterError):
    def __init__(obj: Sequence[Dict[str, Any]]):
        super().__init__('\n'.join(x['detail'] for x in obj))


@dataclass
class TwitterUser:
    id: str
    name: Optional[str]
    username: str


@dataclass
class Tweet:
    id: str
    text: str
    user: TwitterUser


class TwitterApi(ApiBase):
    BASE_URL = "https://api.twitter.com/2/"

    def __init__(self, token: str):
        super().__init__(self.BASE_URL)

        self._session.headers['Authorization'] = f'Bearer {token}'

    def get_user(self, name: str) -> TwitterUser:
        obj = self._request_json(f'/users/by/username/{name}')
        data = obj['data']

        return TwitterUser(data['id'], data['name'], name)

    def get_tweet(self, tweet_id: str) -> Tweet:
        obj = self._request_json(f'/tweets/{tweet_id}', expansions='author_id')
        data = obj['data']
        user = obj['includes']['users'][0]

        return Tweet(tweet_id, data['text'], TwitterUser(user['id'], user['name'], user['username']))

    def _request_json(self, endpoint: str, **kwargs):
        req = self._request(endpoint, **kwargs)

        obj = json.loads(req.text)
        if 'errors' in obj:
            raise TwitterApiError(obj['errors'])

        return obj
