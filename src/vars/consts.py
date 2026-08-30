import logging

logging.basicConfig(level=logging.DEBUG)

COUNTER_INTERVAL_SECONDS: int = 20
CLIPABLE_EMOTES_COUNT: int = 100
CLIPABLE_WAIT: int = 10
COMMON_VALUE: int = 1
EMOTE_VALUE: int = 2

STREAMERS: list = ["ohnePixel", "Jynxzi"]
EXCLUDED_WORDS: list = ["the", "no", "yes", "to", "a", "is", "67"]

TWITCH_OAUTH2_URL: str = "https://id.twitch.tv/oauth2"
TWITCH_HELIX_URL: str = "https://api.twitch.tv/helix"

SEVENTV_URL: str = "https://7tv.io/v3"
