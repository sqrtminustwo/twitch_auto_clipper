from utils.utils import now_formated
from vars.consts import CSV_QUOTING, OUTPUT_DIR

import csv
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path
from threading import Lock


class Logger:
    def __open_writer(self, csvfile):
        return csv.DictWriter(csvfile, fieldnames=self.fieldnames, quoting=CSV_QUOTING)

    def __init__(self, type_to_log, dir=OUTPUT_DIR, filename=f"{now_formated()}.csv"):
        assert is_dataclass(type_to_log)
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
