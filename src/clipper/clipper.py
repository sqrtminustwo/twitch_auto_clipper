# https://www.educative.io/courses/channels-video-twitch-api-python/get-clips
# https://dev.twitch.tv/docs/api/reference#create-clip

from auth.TwitchAuthTokens import TOKENS
from vars.consts import OUTPUT_DIR, TWITCH_HELIX_URL, CLIPABLE_WAIT
from clipper.clip import Clip
from log.logger import Logger

import logging
import time


CLIP_LOGGER = Logger(Clip)


def clip_and_log(clip: Clip) -> None:
    time.sleep(CLIPABLE_WAIT)
    clip.url = clip_now(clip.broadcaster_id)
    CLIP_LOGGER.write(clip)


def clip_now(broadcaster_id, duration=60) -> str:
    assert duration >= 5 and duration <= 60

    try:
        response = TOKENS.authorized_post(
            f"{TWITCH_HELIX_URL}/clips",
            {"broadcaster_id": broadcaster_id, "duration": duration},
            ok_code=202,
        )
        return response["data"][0]["edit_url"]
    except Exception as e:
        logging.error(f"Failed to create clip for {broadcaster_id}: {e}")
