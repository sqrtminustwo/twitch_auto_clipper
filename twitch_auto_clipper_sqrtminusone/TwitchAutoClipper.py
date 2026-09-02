from twitch_auto_clipper_sqrtminusone.chat.Streamer import Streamer
from twitch_auto_clipper_sqrtminusone.chat.TwitchChatIrc import TwitchChatIRC
from twitch_auto_clipper_sqrtminusone.auth.TwitchAuthTokens import TwitchAuthTokens
from twitch_auto_clipper_sqrtminusone.type_aliases.types import OnClipCallBack
from twitch_auto_clipper_sqrtminusone.TwitchAutoClipperContext import (
    TwitchAutoClipperContext,
)

import logging
from threading import Thread


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
        logging.basicConfig(level=logging_level, handlers=logging_handlers)

        self.__context = TwitchAutoClipperContext(
            tokens=TwitchAuthTokens(client_id, client_secret),
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

    def start(self):
        def streamer_thread(streamer: Streamer) -> None:
            twitch_chat_irc = TwitchChatIRC()
            with twitch_chat_irc as connection:
                connection.listen(streamer)

        self.__threads = [
            Thread(target=streamer_thread, args=(streamer,))
            for streamer in self.__streamers
            if streamer.is_live()
        ]
        for thread in self.__threads:
            thread.start()

    def join(self):
        for thread in self.__threads:
            thread.join()
