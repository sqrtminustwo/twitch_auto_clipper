# https://www.educative.io/courses/channels-video-twitch-api-python/get-clips
# https://dev.twitch.tv/docs/api/reference#create-clip

from auth.TwitchAuthTokens import TOKENS
from vars.consts import TWITCH_HELIX_URL, CLIPABLE_WAIT
from clipper.clip import Clip
from log.logger import Logger

import logging
import time


CLIP_LOGGER = Logger(Clip)


def clip_and_log(clip: Clip, duration=60) -> None:
    assert duration >= 5 and duration <= 60

    time.sleep(CLIPABLE_WAIT)

    try:
        response = TOKENS.authorized_post(
            f"{TWITCH_HELIX_URL}/clips",
            {"broadcaster_id": clip.broadcaster_id, "duration": duration},
            ok_code=202,
        )
        clip.url = response["data"][0]["edit_url"]

        CLIP_LOGGER.write(clip)
    except Exception as e:
        logging.debug(f"Failed to clip_and_log: {e}")
