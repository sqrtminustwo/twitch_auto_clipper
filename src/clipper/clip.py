from dataclasses import dataclass


@dataclass
class Clip:
    url: str
    emote: str
    emote_count: float
    ratio: float

    def __init__(
        self,
        broadcaster_id=-1,
        url=None,
        emote=None,
        emote_count=0,
        ratio=0,
    ):
        self.broadcaster_id = broadcaster_id
        self.url = url
        self.emote = emote
        self.emote_count = emote_count
        self.ratio = ratio

    def __lt__(self, obj: "Clip") -> bool:
        return self.ratio < obj.ratio
