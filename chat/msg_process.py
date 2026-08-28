import vars.consts as consts
from sortedcollections.recipes import ValueSortedDict
from vars.emotes import emotes
from utils.utils import now
from vars.consts import CLIPABLE_EMOTES_COUNT, COUNTER_INTERVAL_SECONDS, EXCLUDED_WORDS

WORDS_DICT: ValueSortedDict = ValueSortedDict()
start_of_snapshot = now()


def msg_process(msg: str) -> None:
    global start_of_snapshot

    words = msg.split(" ")
    done = False

    for word in words:
        word_lower = word.lower()
        if word_lower in EXCLUDED_WORDS:
            continue

        value = consts.COMMON_VALUE
        if word in emotes:
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
        if consts.DEBUG and words:
            print("\n====================================")
            most_used = WORDS_DICT.peekitem(index=-1)
            _, count = most_used
            print(f"SNAPSHOT {now_}: {most_used}")
            print(f"clipable = {count > CLIPABLE_EMOTES_COUNT}")
            print("====================================\n")
        WORDS_DICT.clear()
        start_of_snapshot = now_

    if consts.DEBUG and WORDS_DICT:
        print(WORDS_DICT.peekitem(index=-1))
