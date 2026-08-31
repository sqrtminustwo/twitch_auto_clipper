from dataclasses import dataclass


@dataclass
class Clip:
    streamer: str
    url: str
    emote: str = None
    emote_count: int = 0
    ratio: int = 0

    def __init__(self, url):
        self.url = url
