import logging

logging.basicConfig(level=logging.INFO)

COUNTER_INTERVAL_SECONDS: int = 20
CLIPABLE_EMOTES_RATIO: float = 0.5
CLIPABLE_WAIT: int = 10
COMMON_VALUE: int = 1
EMOTE_VALUE: int = 2

STREAMERS_NAMES: list = ["ohnePixel", "Jynxzi", "jasontheween"]
EXCLUDED_WORDS: list = ["the", "no", "yes", "to", "a", "is", "67"]

TWITCH_OAUTH2_URL: str = "https://id.twitch.tv/oauth2"
TWITCH_HELIX_URL: str = "https://api.twitch.tv/helix"

SEVENTV_URL: str = "https://7tv.io/v3"
