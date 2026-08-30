import vars.consts as consts
from utils.utils import now
from vars.Streamer import Streamer
from vars.consts import CLIPABLE_EMOTES_COUNT, COUNTER_INTERVAL_SECONDS, EXCLUDED_WORDS

from sortedcollections.recipes import ValueSortedDict
import logging


WORDS_DICT: ValueSortedDict = ValueSortedDict()
start_of_snapshot = now()


def msg_process(msg: str, streamer: Streamer) -> None:
    global start_of_snapshot

    words = msg.split(" ")
    done = False

    for word in words:
        word_lower = word.lower()
        if word_lower in EXCLUDED_WORDS:
            continue

        value = consts.COMMON_VALUE
        if word in streamer.seventv_emotes:
            value = consts.EMOTE_VALUE
            done = True

        if word_lower in WORDS_DICT:
            WORDS_DICT[word_lower] += value
        else:
            WORDS_DICT[word_lower] = value

        # Avoid emote spam from one user
        if done:
            break

    now_ = now()
    if (now_ - start_of_snapshot).total_seconds() > COUNTER_INTERVAL_SECONDS:
        if words:
            print("\n====================================")
            most_used = WORDS_DICT.peekitem(index=-1)
            _, count = most_used
            print(f"SNAPSHOT {now_}: {most_used}")
            print(f"clipable = {count > CLIPABLE_EMOTES_COUNT}")
            print("====================================\n")

            # TODO: make a clip
            # wait for CLIPABLE_DELAY
            # call clip_now
            # save timestamp and clip url to log file

        WORDS_DICT.clear()
        start_of_snapshot = now_

    if WORDS_DICT:
        logging.debug(WORDS_DICT.peekitem(index=-1))
