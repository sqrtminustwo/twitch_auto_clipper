# https://www.educative.io/courses/channels-video-twitch-api-python/get-clips
# https://dev.twitch.tv/docs/api/reference#create-clip

from auth.TwitchAuthTokens import TOKENS
from vars.consts import TWITCH_HELIX_URL
from clipper.clip import Clip

import logging


def clip_now(broadcaster_id, duration=60) -> Clip:
    assert duration >= 5 and duration <= 60

    try:
        response = TOKENS.authorized_post(
            f"{TWITCH_HELIX_URL}/clips",
            {"broadcaster_id": broadcaster_id, "duration": duration},
            ok_code=202,
        )
        return Clip(response["data"][0]["edit_url"])
    except Exception as e:
        logging.error(f"Failed to create clip for {broadcaster_id}: {e}")
