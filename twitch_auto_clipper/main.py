from TwitchAutoClipper import TwitchAutoClipper

from dotenv import load_dotenv
from os import getenv
import logging

load_dotenv()

clipper = TwitchAutoClipper(
    ["Marlon", "Lacy"],
    getenv("client_id"),
    getenv("client_secret"),
    on_clip=lambda clip: print(clip),
    clipable_message_ratio=0.1,
    logging_level=logging.DEBUG,
)

clipper.start()
clipper.join()
