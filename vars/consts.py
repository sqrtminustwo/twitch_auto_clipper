from dotenv import load_dotenv
from os import getenv

DEBUG: bool = True
COUNTER_INTERVAL_SECONDS: int = 20
CLIPABLE_EMOTES_COUNT: int = 100
COMMON_VALUE: int = 1
EMOTE_VALUE: int = 2

STREAMERS: list = ["ohnePixel"]
EXCLUDED_WORDS = ["the", "no", "yes", "to", "a", "67"]

TWITCH_OAUTH2_URL = "https://id.twitch.tv/oauth2"

load_dotenv()

CLIENT_ID = getenv("client_id")
CLIENT_SECRET = getenv("client_secret")
