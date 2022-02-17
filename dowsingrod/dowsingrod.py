from random import randrange, choice
from math import ceil
from dataclasses import dataclass
from typing import Optional, Sequence, Dict, Any
from redis import Redis
from furl import furl
from flask import Flask

from dowsingrod.danbooru import DanbooruApi
from dowsingrod.twitter import TwitterApi, TwitterUser, TwitterApiError
from dowsingrod.pixiv import PixivEmbedApi, PixivNotFoundError
from dowsingrod.cache import Cache, DumbCache, RedisCache


class DowsingFailure(Exception):
    pass


@dataclass
class Image:
    id: int
    source_type: str
    source: Optional[str]
    artist_url: Optional[str]
    artist_name: Optional[str]
    image: str
    image_preview: str
    image_ext: str


@dataclass
class TreasureSource:
    url: Optional[str]
    artist_url: Optional[str]
    artist_name: Optional[str]
    type: str


@dataclass
class Artist:
    name: str
    url: str


@dataclass
class TwitterSource:
    user: Optional[str]
    tweet_id: Optional[str]


class DowsingRod:
    # TODO: clean up this class, it's a fucking mess right now

    POSTS_PER_REQ = 20

    PIXIV_DOMAINS = ['pximg.net', 'pixiv.net']
    TWITTER_DOMAINS = ['twitter.com']
    SEIGA_DOMAINS = ['seiga.nicovideo.jp']

    EXPIRE_IN = 60 * 60 * 48  # 48 hours

    def __init__(
        self,
        app: Optional[Flask] = None,
        tags: Optional[Sequence[str]] = [],
        twitter_key: Optional[str] = None,
        redis_args: Dict[str, Any] = {}
    ):
        self.danbooru = DanbooruApi()
        self.pixiv = PixivEmbedApi()
        self.twitter = None
        self._tags = tags

        if app:
            self.init_app(app, redis_args)
        else:
            self.twitter = TwitterApi(twitter_key)
            self._cache = DumbCache()

    def init_app(self, app: Flask, redis_args: Dict[str, Any] = {}):
        config = app.config['DOWSINGROD']

        self._tags = config.get('tags', self._tags)
        twitter_key = config.get('twitter_bearer_token')
        if not twitter_key:
            raise DowsingFailure(f'Twitter API key was not present in Flask config')

        self.twitter = TwitterApi(twitter_key)
        self._cache = RedisCache(config.get('redis_url', 'redis://localhost:6379/0'), **redis_args)

    def find_treasure(self) -> Image:
        post_count = self.danbooru.count_posts(self._tags)
        pages = ceil(post_count / self.POSTS_PER_REQ)

        page = randrange(0, pages + 1)

        posts = self.danbooru.posts(self._tags, page=page)
        post = choice(posts)

        artist_name = None
        artist_url = None
        source_url = post.source or None
        source_type = "other"

        if post.source:
            src = self._cache.get(f'SOURCE_{post.id}')

            if not src:
                src = self._resolve_source(post.source or '')

                if src:
                    self._cache.set(f'SOURCE_{post.id}', src, expire=self.EXPIRE_IN)

            if src:
                artist_name = src.artist_name
                artist_url = src.artist_url
                source_url = src.url
                source_type = src.type

        return Image(post.id,
                     source_type,
                     source_url,
                     artist_url,
                     artist_name,
                     post.large_file_url,
                     post.preview_file_url,
                     post.file_ext)

    def _resolve_source(self, src_url: str) -> Optional[TreasureSource]:
        f = furl(src_url)
        def match(seq: Sequence[str]) -> bool:
            return any(f.host.endswith(x) for x in seq)

        src = None

        if match(self.PIXIV_DOMAINS):
            art_id = self._parse_pixiv_url(src_url)
            try:
                user = self._cache.get(f'PIXIV_{art_id}')

                if not user:
                    user = self._resolve_pixiv_user(art_id)
                    self._cache.set(f'PIXIV_{art_id}', user, expire=self.EXPIRE_IN)

                src = TreasureSource(f'https://pixiv.net/artworks/{art_id}', user.url, user.name, 'pixiv')
            except PixivNotFoundError:
                #src = TreasureSource(src_url, None, None, 'pixiv')
                pass
        elif match(self.TWITTER_DOMAINS):
            twsrc = self._parse_twitter_url(src_url)

            user = None

            if twsrc.user:
                user = self._cache.get(f'TWITTER_USER_{twsrc.user}')
            elif twsrc.tweet_id:
                user = self._cache.get(f'TWITTER_TWEET_{twsrc.tweet_id}')

            if not user:
                try:
                    user = self._resolve_twitter_user(twsrc)

                    if not user:
                        return None

                    self._cache.set(f'TWITTER_USER_{twsrc.user}', user, expire=self.EXPIRE_IN)
                    self._cache.set(f'TWITTER_TWEET_{twsrc.tweet_id}', user, expire=self.EXPIRE_IN)
                except TwitterApiError:
                    return None

            twurl = f'https://twitter.com/i/status/{twsrc.tweet_id}' if twsrc.tweet_id is not None else src_url

            if user:
                src = TreasureSource(twurl, user.url, user.name, 'twitter')
            else:
                src = TreasureSource(twurl, f'https://twitter.com/{twsrc.user}', twsrc.user, 'twitter')
        elif match(self.SEIGA_DOMAINS):
            # TODO
            src = TreasureSource(src_url, None, None, 'seiga')

        return src

    def _resolve_pixiv_user(self, image_id: str) -> Artist:
        art = self.pixiv.get_artwork(image_id)

        return Artist(art.author_name, f'https://pixiv.net/users/{art.author_id}')


    def _resolve_twitter_user(self, src: TwitterSource) -> Optional[TwitterUser]:
        if src.tweet_id is None and src.user is None:
            return None

        user = None

        if src.tweet_id:
            user = self.twitter.get_tweet(src.tweet_id).user
        elif src.user:
            user = self.twitter.get_user(src.user)

        if user:
            return Artist(user.name, f'https://twitter.com/i/user/{user.id}')
        else:
            return None


    def _parse_seiga_url(self, url: str) -> str:
        f = furl(url)

        if not any(f.host.endswith(x) for x in self.SEIGA_DOMAINS):
            raise DowsingFailure("URL is not a valid NicoNicoSeiga URL")

        return f.path.segments[-1]

    def _parse_twitter_url(self, url: str) -> TwitterSource:
        f = furl(url)

        if not any(f.host.endswith(x) for x in self.TWITTER_DOMAINS):
            raise DowsingFailure('URL is not a valid Twitter URL')

        segs = f.path.segments

        if len(segs) > 1 and segs[1] == "status":
            tweet_id = segs[2] if len(segs) == 3 else None
            user = segs[0] if segs[0] and segs[0] != 'i' else None

            return TwitterSource(user, tweet_id)
        else:
            return TwitterSource(None, None)


    def _parse_pixiv_url(self, url: str) -> str:
        f = furl(url)

        if not any(f.host.endswith(x) for x in self.PIXIV_DOMAINS):
            raise DowsingFailure('URL is not a valid Pixiv URL')

        file = f.path.segments[-1]
        post_id = file.split('_')[0].split(".")[0]

        return post_id


