from twitch_auto_clipper.TwitchAutoClipper import TwitchAutoClipper

from dotenv import load_dotenv
from os import getenv

load_dotenv()


def on_clip(clip):
    print(clip.message)
    print(clip.url)


clipper = TwitchAutoClipper(
    ["Marlon", "Lacy"],
    getenv("client_id"),
    getenv("client_secret"),
    on_clip=on_clip,
    common_value=1,
    emote_value=2,
    clipable_message_ratio=0.1,
)

clipper.start()
clipper.join()
