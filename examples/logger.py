from twitch_auto_clipper.TwitchAutoClipper import TwitchAutoClipper
from twitch_auto_clipper.utils.utils import now_formated
from twitch_auto_clipper.clip.Clip import Clip

import csv
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path
from threading import Lock
from dotenv import load_dotenv
import os


class Logger:
    def __open_writer(self, csvfile):
        return csv.DictWriter(
            csvfile, fieldnames=self.fieldnames, quoting=csv.QUOTE_NONNUMERIC
        )

    def __init__(self, type_to_log, dir=Path("log"), filename=f"{now_formated()}.csv"):
        assert is_dataclass(type_to_log)

        os.makedirs(dir, exist_ok=True)

        self.type = type_to_log
        self.path = Path(dir, filename)
        self.fieldnames = [field.name for field in fields(type_to_log)]
        self.file_lock = Lock()

        with open(self.path, "w+") as csvfile:
            writer = self.__open_writer(csvfile)
            writer.writeheader()

    def write(self, data):
        assert type(data) is self.type
        with self.file_lock:
            with open(self.path, "a") as csvfile:
                writer = self.__open_writer(csvfile)
                writer.writerow(asdict(data))


load_dotenv()

CLIP_LOGGER = Logger(Clip)


def on_clip(clip):
    CLIP_LOGGER.write(clip)


clipper = TwitchAutoClipper(
    ["Marlon", "Lacy"],
    os.getenv("client_id"),
    os.getenv("client_secret"),
    on_clip=on_clip,
    common_value=1,
    emote_value=2,
    clipable_message_ratio=0.5,
)

clipper.start()
clipper.join()
