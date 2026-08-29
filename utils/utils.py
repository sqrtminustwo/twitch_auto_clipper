from datetime import datetime
from threading import Condition
from contextlib import contextmanager


def now() -> datetime:
    return datetime.now()


class ProtectedVar:
    def __init__(self, var=None):
        self.__var = var
        self.condition = Condition()

    def wait(self, condition=lambda var: var is not None):
        with self.condition:
            while not condition(self.__var):
                self.condition.wait()

    def set(self, val):
        with self.condition:
            self.__var = val
            self.condition.notify_all()

    def get(self):
        with self.condition:
            return self.__var

    @contextmanager
    def protecting(self, a, b):
        with self.condition:
            waited = False
            while self.__var == a:
                waited = True
                self.wait(condition=lambda var: var == b)

            if waited:
                yield True
                return

            # cant call set because inside with
            # cant place outside with because of race conditions
            self.__var = a
            self.condition.notify_all()

        try:
            yield False
        finally:
            self.set(b)
