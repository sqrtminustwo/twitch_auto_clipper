from clipper.clip import Clip
from vars.consts import CSV_QUOTING, OUTPUT_DIR
from log.logger import Logger

from dacite import from_dict
import csv
import sys
import os

assert len(sys.argv) == 2, "No file passed"
file_name: str = sys.argv[1]

clips = []
with open(file_name, mode="r") as file:
    reader = csv.DictReader(file, quoting=CSV_QUOTING)
    for row in reader:
        clip = from_dict(data_class=Clip, data=row)
        clips.append(clip)

clips.sort(reverse=True)

file_name = os.path.basename(file_name)
name, extension = file_name.split(".")
logger = Logger(Clip, filename=f"{name}_sorted.{extension}")

for clip in clips:
    logger.write(clip)
