# https://www.educative.io/courses/channels-video-twitch-api-python/get-clips
# https://dev.twitch.tv/docs/api/reference#create-clip

from vars.Streamer import Streamer
from auth import TwitchAuthTokens
from vars.consts import TWITCH_HELIX_URL

import logging


def clip_now(streamer: Streamer, tokens: TwitchAuthTokens, duration=60) -> str:
    assert duration >= 5 and duration <= 60

    try:
        response = tokens.authorized_post(
            f"{TWITCH_HELIX_URL}/clips",
            {"broadcaster_id": streamer.id, "duration": duration},
            ok_code=202,
        )
        return response["data"][0]["edit_url"]
    except Exception as e:
        logging.error(f"Failed to create clip for {streamer.login}: {e}")
