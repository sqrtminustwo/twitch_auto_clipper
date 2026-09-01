from auth.TwitchAuthTokens import TOKENS
from vars.consts import (
    COMMON_VALUE,
    EMOTE_VALUE,
    TWITCH_HELIX_URL,
    SEVENTV_URL,
    STREAMERS_NAMES,
    EXCLUDED_WORDS,
    COUNTER_INTERVAL_SECONDS,
    CLIPABLE_EMOTES_RATIO,
)
from clipper.clipper import clip_and_log
from clipper.clip import Clip
from utils.utils import now

import requests
import logging
from sortedcollections.recipes import ValueSortedDict
from threading import Thread


class Streamer:
    def __init__(self, login, platform="twitch"):
        self.login = login
        self.platform = platform
        self.id = None
        self.seventv_emotes = set()

        self.words_dict: ValueSortedDict = ValueSortedDict()
        self.message_count: int = 0
        self.clipping_thread: Thread = None
        self.start_of_snapshot = None

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
        logging.info(f"{self} is {'' if live else 'not '}live")
        return live

    def on_message(self, msg: str) -> None:
        # set to avoid spam messages
        words = set(msg.split(" "))

        for word in words:
            word_lower = word.lower()
            if word_lower in EXCLUDED_WORDS:
                continue

            value = self.get_message_value(word)

            if word_lower in self.words_dict:
                self.words_dict[word_lower] += value
            else:
                self.words_dict[word_lower] = value

        # if self.words_dict:
        # logging.debug(f"{self}: {self.words_dict.peekitem(index=-1)}")

        self.take_snapshot_if_time()

    def take_snapshot_if_time(self) -> None:
        self.message_count += 1

        now_ = now()
        if (now_ - self.start_of_snapshot).total_seconds() > COUNTER_INTERVAL_SECONDS:
            if self.words_dict:
                logging.info("====================================")
                most_used = self.words_dict.peekitem(index=-1)
                emote, count = most_used
                # ration can be larger than 1, emojies have higher count than 1
                ratio_to_all = count / self.message_count
                clipable = ratio_to_all > CLIPABLE_EMOTES_RATIO
                logging.info(f"SNAPSHOT for {self} at {now_}: {most_used}")
                logging.info(f"{ratio_to_all = }, {count = }, {self.message_count = }")
                logging.info(f"{clipable = }")
                logging.info("====================================\n")

                if clipable:
                    if self.clipping_thread and self.clipping_thread.is_alive():
                        self.clipping_thread.join()

                    clip: Clip = Clip(
                        broadcaster_id=self.id,
                        emote=emote,
                        emote_count=count,
                        ratio=ratio_to_all,
                    )
                    self.clipping_thread = Thread(target=clip_and_log, args=(clip,))
                    self.clipping_thread.start()

                self.message_count = 0
                self.words_dict.clear()
                self.start_of_snapshot = now_


STREAMERS: list = [Streamer(name) for name in STREAMERS_NAMES]
