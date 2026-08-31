from dataclasses import dataclass


@dataclass
class Clip:
    url: str
    emote: str
    emote_count: int

    def __init__(self, url, emote=None, emote_count=0):
        self.url = url
        self.emote = emote
        self.emote_count = emote_count
