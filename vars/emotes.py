import requests
from vars.consts import STREAMERS

emotes: set = set()

SEVENTV_BASE: str = "https://7tv.io/v3"

TWITCH_TO_SEVENTV: dict = {STREAMERS[0]: "01G6ZWWNV00009H0PZMRY832FZ"}


def make_emotes_for_twitchname(twitchname: str) -> None:
    try:
        user = requests.get(
            f"{SEVENTV_BASE}/users/{TWITCH_TO_SEVENTV[twitchname]}"
        ).json()
        emote_sets_meta = user["emote_sets"]

        largest_emote_set = []
        for emote_set_meta in emote_sets_meta:
            emote_set = requests.get(
                f"{SEVENTV_BASE}/emote-sets/{emote_set_meta['id']}"
            ).json()["emotes"]
            if len(emote_set) > len(largest_emote_set):
                largest_emote_set = emote_set

        largest_emote_set = [e["name"] for e in largest_emote_set]

        emotes.clear()
        emotes.update(largest_emote_set)

    except Exception as e:
        print(f"Failed to make emotes for {twitchname}:\n{e}")
