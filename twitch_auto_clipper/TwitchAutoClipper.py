from twitch_auto_clipper.chat.Streamer import Streamer
from twitch_auto_clipper.chat.TwitchChatIRC import TwitchChatIRC
from twitch_auto_clipper.auth.TwitchAuthTokens import TwitchAuthTokens
from twitch_auto_clipper.type_aliases.types import OnClipCallBack
from twitch_auto_clipper.TwitchAutoClipperContext import (
    TwitchAutoClipperContext,
)

import logging
from threading import Thread
import time

from twitch_auto_clipper.utils.utils import log_delimiter


class TwitchAutoClipper:
    def __init__(
        self,
        streamers_names: list[str],
        client_id: str,
        client_secret: str,
        on_clip: OnClipCallBack,
        counter_interval_seconds: int = 20,
        clipable_message_ratio: float = 0.5,
        clipable_wait: int = 10,
        common_value: int = 1,
        emote_value: int = 2,
        excluded_words: set[str] = {"the", "you", "no", "yes", "to", "a", "is", "67"},
        logging_handlers: list[logging.Handler] = [logging.StreamHandler()],
        logging_level=logging.DEBUG,
    ):
        assert streamers_names, f"{streamers_names = }, which is invalid, can't clip!"
        assert client_id, f"{client_id = }, which is invalid, won't be able to clip!"
        assert client_secret, (
            f"{client_secret = }, which is invalid, won't be able to clip!"
        )

        logging.basicConfig(
            level=logging_level,
            handlers=logging_handlers,
            format="%(levelname)s:%(threadName)s: %(message)s",
        )

        self.__context = TwitchAutoClipperContext(
            tokens=TwitchAuthTokens(client_id, client_secret).initialize(),
            on_clip=on_clip,
            excluded_words=excluded_words,
            counter_interval_seconds=counter_interval_seconds,
            clipable_message_ratio=clipable_message_ratio,
            clipable_wait=clipable_wait,
            common_value=common_value,
            emote_value=emote_value,
        )

        logging.info("Initalized context")

        self.__threads = []
        self.__streamers = [Streamer(name, self.__context) for name in streamers_names]

    def __streamer_thread(self, i) -> None:
        with self.__chats[i] as connection:
            connection.listen(self.__streamers[i])

    def start(self):
        live_streamers = [
            streamer for streamer in self.__streamers if streamer.is_live()
        ]
        self.__chats = [TwitchChatIRC() for _ in range(len(live_streamers))]
        self.__threads = [
            Thread(target=self.__streamer_thread, name=streamer, args=(i,))
            for i, streamer in enumerate(live_streamers)
        ]

        for thread in self.__threads:
            thread.start()

    def __join_streamer_threads(self):
        for thread in self.__threads:
            thread.join()

    def join(self):
        try:
            # just joining causes first thread to exit silently
            # without closing anything, i debugged this for 5 hours,
            # 95% shure its a python bug, or im just ass at multithreading
            # (later is more likely)
            for chat in self.__chats:
                chat.finished_wait(timeout=None, condition=lambda finished: finished)
        except KeyboardInterrupt:
            log_delimiter()
            logging.info("Interrupted, finishing all clips.")

            for streamer in self.__streamers:
                streamer.stop_listening.value = True

        finally:
            self.__join_streamer_threads()
