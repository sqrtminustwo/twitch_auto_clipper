from datetime import datetime


def now() -> datetime:
    return datetime.now()


def now_formated() -> datetime:
    return now().strftime("%d-%m-%Y_%H:%M:%S")
