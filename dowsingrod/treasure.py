from random import randrange, choice
from math import ceil
from dataclasses import dataclass
from dowsingrod.danbooru import Danbooru


@dataclass
class Image:
    id: int
    source: str
    artist_url: str
    artist_name: str
    image: str
    image_preview: str


class Treasure:
    POSTS_PER_REQ = 20

    def __init__(self, app, tags: list[str]):
        self.api = Danbooru()
        self.tags = tags

    def random_image(self) -> Image:
        post_count = self.api.count_posts(self.tags)
        pages = ceil(post_count / self.POSTS_PER_REQ)

        page = randrange(0, pages + 1)

        posts = self.api.posts(self.tags, page=page)
        post = choice(posts)

        return Image(post.id)


