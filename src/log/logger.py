from utils.utils import now

import csv
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path
from threading import Lock


class Logger:
    def __open_writer(self, csvfile):
        return csv.DictWriter(csvfile, fieldnames=self.fieldnames)

    def __init__(self, dir, type_to_log):
        assert is_dataclass(type_to_log)
        self.type = type_to_log
        self.path = Path(dir, f"{now().strftime('%d-%m-%Y_%H:%M:%S')}.csv")
        self.fieldnames = [field.name for field in fields(type_to_log)]
        self.file_lock = Lock()

        print(self.fieldnames)

        with open(self.path, "w+") as csvfile:
            writer = self.__open_writer(csvfile)
            writer.writeheader()

    def write(self, data):
        assert type(data) is self.type
        with self.file_lock:
            with open(self.path, "a") as csvfile:
                writer = self.__open_writer(csvfile)
                writer.writerow(asdict(data))
