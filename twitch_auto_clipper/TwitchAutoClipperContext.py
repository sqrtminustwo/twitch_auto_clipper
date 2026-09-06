from twitch_auto_clipper.auth.TwitchAuthTokens import TwitchAuthTokens
from twitch_auto_clipper.type_aliases.types import OnClipCallBack

from dataclasses import dataclass


@dataclass
class TwitchAutoClipperContext:
    tokens: TwitchAuthTokens
    on_clip: OnClipCallBack
    counter_interval_seconds: int
    clipable_message_ratio: float
    clipable_wait: int
    common_value: int
    emote_value: int
    excluded_words: set[str]
