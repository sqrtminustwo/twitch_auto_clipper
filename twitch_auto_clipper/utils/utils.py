from datetime import datetime
import logging


def log_delimiter(above=True):
    delimiter = "===================================="
    if not above:
        delimiter += "\n"

    logging.info(delimiter)


def now_formated(datetime=datetime) -> datetime:
    return datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
