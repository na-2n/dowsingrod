import requests

from random import randrange, choice
from math import ceil
from dataclasses import dataclass
from typing import Optional
from furl import furl

from dowsingrod.danbooru import DanbooruApi
from dowsingrod.twitter import TwitterApi, TwitterUser
from dowsingrod.pixiv import PixivEmbedApi, PixivNotFoundError


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
    POSTS_PER_REQ = 20

    PIXIV_DOMAINS = ['pximg.net', 'pixiv.net']
    TWITTER_DOMAINS = ['twitter.com']
    SEIGA_DOMAINS = ['seiga.nicovideo.jp']

    def __init__(self, tags: list[str], twitter_key: str):
        self.danbooru = DanbooruApi()
        self.twitter = TwitterApi(twitter_key)
        self.pixiv = PixivEmbedApi()
        self._session = requests.Session()
        self._tags = tags

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
            src = self._resolve_source(post.source)

            if src:
                artist_name = src.artist_name
                artist_url = src.artist_url
                source_url = src.url
                source_type = src.type

        return Image(post.id, source_type, source_url, artist_url, artist_name, post.large_file_url, post.preview_file_url)

    def _resolve_source(self, src_url: str) -> Optional[TreasureSource]:
        f = furl(src_url)
        match = lambda seq: any(f.host.endswith(x) for x in seq)

        src = None

        if match(self.PIXIV_DOMAINS):
            art_id = self._parse_pixiv_url(src_url)
            try:
                user = self._resolve_pixiv_user(art_id)

                src = TreasureSource(f'https://pixiv.net/artworks/{art_id}', user.url, user.name, 'pixiv')
            except PixivNotFoundError:
                #src = TreasureSource(src_url, None, None, 'pixiv')
                pass
        elif match(self.TWITTER_DOMAINS):
            twsrc = self._parse_twitter_url(src_url)
            user = self._resolve_twitter_user(twsrc)

            twurl = f'https://twitter.com/i/status/{twsrc.tweet_id}' if twsrc.tweet_id is not None else None

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
            user = segs[0] if segs[0] else None

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


