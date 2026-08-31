from auth.TwitchAuthTokens import TOKENS
from vars.consts import COMMON_VALUE, EMOTE_VALUE, TWITCH_HELIX_URL, SEVENTV_URL

import requests
import logging


class Streamer:
    def __init__(self, login, platform="twitch"):
        self.login = login
        self.platform = platform
        self.id = None
        self.seventv_emotes = set()

    # https://dev.twitch.tv/docs/api/reference/#get-users
    def initialize(self) -> "Streamer":
        self.__initialize_id()
        self.__initialize_seventv_emotes()

        logging.info(f"Initialized {self}")

        return self

    def __initialize_id(self):
        # no catch because critical
        response = TOKENS.authorized_get_json(
            f"{TWITCH_HELIX_URL}/users",
            params={"login": self.login},
        )
        self.id = response["data"][0]["id"]

        logging.debug(f"Initialized id for {self}")

    def get_message_value(self, msg):
        if msg in self.seventv_emotes or msg.lower() in self.seventv_emotes:
            return EMOTE_VALUE
        return COMMON_VALUE

    def __initialize_seventv_emotes(self):
        # catch because optional
        try:
            response: requests.Response = requests.get(
                f"{SEVENTV_URL}/users/{self.platform}/{self.id}"
            )
            response = response.json()

            emotes = response["emote_set"]["emotes"]
            self.seventv_emotes.clear()
            self.seventv_emotes.update([emote["name"] for emote in emotes])

            logging.debug(f"Initialized emotes for {self}")
        except Exception:
            pass

    def __repr__(self):
        return f"{self.__class__.__name__}({self.login})"

    def is_live(self):
        params = {}
        if self.id:
            params["user_id"] = self.id
        if self.login:
            params["user_login"] = self.login

        response = TOKENS.authorized_get_json(f"{TWITCH_HELIX_URL}/streams", params)
        live = len(response["data"]) > 0
        logging.info(f"{self} is {'' if live else 'not'} live")
        return live
