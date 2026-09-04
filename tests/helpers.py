from collections.abc import Callable
from threading import Thread
from time import sleep


def id(v):
    return v


def create_threads(func: Callable[[None], None]) -> list[Thread]:
    return [Thread(target=func) for _ in range(5)]


def start_all(threads: list[Thread]):
    for thread in threads:
        thread.start()


def join_all(threads: list[Thread]):
    for thread in threads:
        thread.join()


def sleep_conditionally(cond):
    if cond:
        sleep(1)


def for_testing_protected(func: Callable[[None], None], done) -> list[Thread]:
    refresh_threads = create_threads(func)
    refresh_threads[0].start()

    while True:
        if done.is_waiting():
            break

    for i in range(1, len(refresh_threads)):
        refresh_threads[i].start()

    return refresh_threads
