from twitch_auto_clipper.utils.ProtectedVar import ProtectedVar
from twitch_auto_clipper.chat.Message import Message
from twitch_auto_clipper.Urls import Urls
from twitch_auto_clipper.TwitchAutoClipperContext import (
    TwitchAutoClipperContext,
)
from twitch_auto_clipper.clip.Clip import Clip
from twitch_auto_clipper.utils.utils import log_delimiter

from datetime import datetime
import time
import requests
import logging
from sortedcollections.recipes import ValueSortedDict
from threading import Thread


class StopListeningException(Exception):
    pass


class Streamer:
    def __init__(
        self,
        login,
        context: TwitchAutoClipperContext,
        platform: str = "twitch",
        requests=requests,
    ):
        assert isinstance(platform, str)

        self.login = login
        self.context = context
        self.platform = platform
        self.__requests = requests

        self.id = None
        self.seventv_emotes = set()

        self.words_dict: ValueSortedDict = ValueSortedDict()
        self.message_count: int = 0
        self.clipping_thread: Thread = None
        self.start_of_snapshot = None

        self.stop_listening = ProtectedVar(False)

        self.__initialize_id()
        self.__initialize_seventv_emotes()

        logging.info(f"Initialized {self}")

    def __initialize_id(self):
        # no catch because critical
        response = self.context.tokens.authorized_get_json(
            f"{Urls.TWITCH_HELIX_URL}/users",
            params={"login": self.login},
        )
        self.id = response["data"][0]["id"]

        logging.debug(f"Initialized id for {self}")

    def __initialize_seventv_emotes(self):
        # catch because optional
        try:
            response: requests.Response = self.__requests.get(
                f"{Urls.SEVENTV_URL}/users/{self.platform}/{self.id}"
            )
            response = response.json()

            emotes = response["emote_set"]["emotes"]
            self.seventv_emotes.clear()
            self.seventv_emotes.update([emote["name"].lower() for emote in emotes])

            logging.debug(f"Initialized emotes for {self}")
        except Exception:
            pass

    def __repr__(self):
        return self.login

    def is_live(self):
        params = {}
        if self.id:
            params["user_id"] = self.id
        if self.login:
            params["user_login"] = self.login

        response = self.context.tokens.authorized_get_json(
            f"{Urls.TWITCH_HELIX_URL}/streams", params
        )
        live = len(response["data"]) > 0
        logging.info(f"{self} is {'' if live else 'not '}live")
        return live

    def clip(self, clip: Clip) -> None:
        time.sleep(self.context.clipable_wait)

        try:
            clip.set_timestamp(datetime.now())
            response = self.context.tokens.authorized_post_json(
                f"{Urls.TWITCH_HELIX_URL}/clips",
                {"broadcaster_id": clip.broadcaster_id, "duration": clip.duration},
                ok_code=202,
            )
            clip.url = response["data"][0]["edit_url"]

            self.context.on_clip(clip)
        except Exception as e:
            logging.debug(f"Failed to clip_and_log: {e}")

    def get_message_value(self, msg):
        if msg.lower() in self.seventv_emotes:
            return self.context.emote_value
        return self.context.common_value

    @property
    def most_used(self):
        if self.words_dict:
            return self.words_dict.peekitem(index=-1)

    def __join_clipping_thread(self):
        if self.clipping_thread and self.clipping_thread.is_alive():
            logging.info(f"Finishing clipping in {self}...")
            self.clipping_thread.join()
            logging.info(f"Done clipping in {self}.")

    def on_message(self, msg: str) -> None:
        if self.stop_listening.value:
            self.__join_clipping_thread()
            raise StopListeningException()

        # set to avoid spam messages
        words = set(msg.lower().split(" "))

        for word in words:
            word = Message(word)

            if word in self.context.excluded_words:
                continue

            value = self.get_message_value(word)

            if word in self.words_dict:
                self.words_dict[word] += value
            else:
                self.words_dict[word] = value

        if self.words_dict:
            logging.debug(self.most_used)

        self.message_count += 1
        now_ = datetime.now()

        message, count = self.most_used
        # ration can be larger than 1, emojies have higher count than 1
        ratio_to_all = count / self.message_count
        clipable = ratio_to_all >= self.context.clipable_message_ratio

        if clipable and message.became_popular is None:
            message.became_popular = now_

        if (
            now_ - self.start_of_snapshot
        ).total_seconds() > self.context.counter_interval_seconds:
            if self.words_dict:
                log_delimiter()
                logging.info(f"SNAPSHOT for {self} at {now_}: {self.most_used}")
                logging.info(f"{ratio_to_all = }, {count = }, {self.message_count = }")
                logging.info(f"{clipable = }")
                log_delimiter(above=False)

                if clipable:
                    self.__join_clipping_thread()

                    clip: Clip = Clip(
                        broadcaster_id=self.id,
                        message=message,
                        message_count=count,
                        ratio=ratio_to_all,
                    )
                    self.clipping_thread = Thread(target=self.clip, args=(clip,))
                    self.clipping_thread.start()

                self.message_count = 0
                self.words_dict.clear()
                self.start_of_snapshot = now_
