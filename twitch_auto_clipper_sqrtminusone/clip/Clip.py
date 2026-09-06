from twitch_auto_clipper_sqrtminusone.chat.Message import Message

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Clip:
    MAX_CLIP_LENGTH = 60
    message: Message  # will be cast to str, trust
    message_count: float
    ratio: float
    broadcaster_id: int = field(repr=False)
    url: str = field(default=None)
    timestamp: datetime = field(default=None)
    duration: float = field(repr=False, default=MAX_CLIP_LENGTH)

    def set_timestamp(self, clip_time: datetime):
        diff = (clip_time - self.message.became_popular).total_seconds()
        # twitch say they capture 5 sec after the timestamp on which we called
        self.timestamp = self.duration - 5 - diff

    # to make list of Clip's sortable
    def __lt__(self, obj: "Clip") -> bool:
        return self.ratio < obj.ratio
