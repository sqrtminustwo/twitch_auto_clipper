from twitch_auto_clipper_sqrtminusone.TwitchAutoClipper import TwitchAutoClipper

from dotenv import load_dotenv
from os import getenv

load_dotenv()

clipper = TwitchAutoClipper(
    ["Marlon", "Lacy"],
    getenv("client_id"),
    getenv("client_secret"),
    on_clip=lambda clip: print(clip),
    common_value=1,
    emote_value=2,
    clipable_message_ratio=0.2,
)

clipper.start()
clipper.join()
