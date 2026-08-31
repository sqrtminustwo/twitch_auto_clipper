from utils.utils import now
from chat.Streamer import Streamer
from vars.consts import (
    CLIPABLE_EMOTES_RATIO,
    CLIPABLE_WAIT,
    COUNTER_INTERVAL_SECONDS,
    EXCLUDED_WORDS,
)
from log.logger import Logger
from clipper.clip import Clip
from clipper.clipper import clip_now

from sortedcollections.recipes import ValueSortedDict
import logging
import time
from threading import Thread


CLIP_LOGGER = Logger("log", Clip)
WORDS_DICT: ValueSortedDict = ValueSortedDict()
message_count: int = 0
start_of_snapshot = now()
clipping_thread: Thread = None


def msg_process(msg: str, streamer: Streamer) -> None:
    # set to avoid spam messages
    words = set(msg.split(" "))

    for word in words:
        word_lower = word.lower()
        if word_lower in EXCLUDED_WORDS:
            continue

        value = streamer.get_message_value(word)

        if word_lower in WORDS_DICT:
            WORDS_DICT[word_lower] += value
        else:
            WORDS_DICT[word_lower] = value

    if WORDS_DICT:
        logging.debug(WORDS_DICT.peekitem(index=-1))

    take_snapshot_if_time(streamer)


def make_clip(streamer: Streamer, emote: str, count: int):
    time.sleep(CLIPABLE_WAIT)
    clip: Clip = clip_now(streamer)
    clip.emote = emote
    clip.emote_count = count
    CLIP_LOGGER.write(clip)


def take_snapshot_if_time(streamer: Streamer) -> None:
    global start_of_snapshot, clipping_thread, message_count

    message_count += 1

    now_ = now()
    if (now_ - start_of_snapshot).total_seconds() > COUNTER_INTERVAL_SECONDS:
        if WORDS_DICT:
            print("\n====================================")
            most_used = WORDS_DICT.peekitem(index=-1)
            emote, count = most_used
            # ration can be larger than 1, emojies have higher count than 1
            ratio_to_all = count / message_count
            clipable = ratio_to_all > CLIPABLE_EMOTES_RATIO
            print(f"SNAPSHOT {now_}: {most_used}")
            logging.info(f"P{ratio_to_all = }, {count = }, {message_count = }")
            print(f"{clipable = }")
            print("====================================\n")

            if clipable:
                if clipping_thread and clipping_thread.is_alive():
                    clipping_thread.join()
                clipping_thread = Thread(
                    target=make_clip, args=(streamer, emote, count)
                )
                clipping_thread.start()

            message_count = 0

        WORDS_DICT.clear()
        start_of_snapshot = now_
