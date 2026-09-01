# https://www.educative.io/courses/channels-video-twitch-api-python/get-clips
# https://dev.twitch.tv/docs/api/reference#create-clip

from auth.TwitchAuthTokens import TOKENS
from vars.consts import TWITCH_HELIX_URL, CLIPABLE_WAIT
from clipper.Clip import Clip
from log.logger import Logger
from utils.utils import now

import logging
import time


CLIP_LOGGER = Logger(Clip)


def clip_and_log(clip: Clip) -> None:
    time.sleep(CLIPABLE_WAIT)

    try:
        clip.set_timestamp(now())
        response = TOKENS.authorized_post(
            f"{TWITCH_HELIX_URL}/clips",
            {"broadcaster_id": clip.broadcaster_id, "duration": clip.duration},
            ok_code=202,
        )
        clip.url = response["data"][0]["edit_url"]

        CLIP_LOGGER.write(clip)
    except Exception as e:
        logging.debug(f"Failed to clip_and_log: {e}")
