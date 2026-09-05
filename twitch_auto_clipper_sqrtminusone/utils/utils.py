from datetime import datetime


def now_formated(datetime=datetime) -> datetime:
    return datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
