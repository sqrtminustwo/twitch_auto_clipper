import logging
from pathlib import Path

from utils.utils import now_formated
import csv

LOGGING_DIR: Path = Path("log")

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler(LOGGING_DIR / "debug" / f"{now_formated()}.txt", mode="a"),
        logging.StreamHandler(),
    ],
)

COUNTER_INTERVAL_SECONDS: int = 20
CLIPABLE_EMOTES_RATIO: float = 0.5
CLIPABLE_WAIT: int = 10
COMMON_VALUE: int = 1
EMOTE_VALUE: int = 2

CSV_QUOTING = csv.QUOTE_NONNUMERIC
OUTPUT_DIR = LOGGING_DIR / "output"

STREAMERS_NAMES: list = ["ohnePixel", "Jynxzi", "ceo_of_zaza"]
DEBUG_STREAMER: int = -1
EXCLUDED_WORDS: set = set(["the", "no", "yes", "to", "a", "is", "67"])

TWITCH_OAUTH2_URL: str = "https://id.twitch.tv/oauth2"
TWITCH_HELIX_URL: str = "https://api.twitch.tv/helix"

SEVENTV_URL: str = "https://7tv.io/v3"
