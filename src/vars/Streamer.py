from auth.TwitchAuthTokens import TwitchAuthTokens
from vars.consts import TWITCH_HELIX_URL, SEVENTV_URL

import requests
import logging


class Streamer:
    def __init__(self, login, platform="twitch"):
        self.login = login
        self.platform = platform
        self.id = None
        self.seventv_emotes = set()

    # https://dev.twitch.tv/docs/api/reference/#get-users
    def initialize(self, tokens: TwitchAuthTokens) -> "Streamer":
        try:
            self.__initialize_id(tokens)
            self.__initialize_seventv_emotes()

            logging.info(f"Initialized {self}")

            return self
        except Exception as e:
            logging.error(f"Failed to initialize {self}: {e}")

    def __initialize_id(self, tokens: TwitchAuthTokens):
        response = tokens.authorized_get_json(
            f"{TWITCH_HELIX_URL}/users",
            params={"login": self.login},
        )
        self.id = response["data"][0]["id"]

        logging.debug(f"Initialized id for {self}")

    def __initialize_seventv_emotes(self):
        response: requests.Response = requests.get(
            f"{SEVENTV_URL}/users/{self.platform}/{self.id}"
        )
        response.raise_for_status()
        response = response.json()

        emotes = response["emote_set"]["emotes"]
        self.seventv_emotes.clear()
        self.seventv_emotes.update([emote["name"] for emote in emotes])

        logging.debug(f"Initialized emotes for {self}")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.login})"
