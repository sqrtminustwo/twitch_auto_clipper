from threading import Condition
from contextlib import contextmanager


class ProtectedVar:
    def __init__(self, var=None):
        self.__var = var
        self.condition = Condition()

        self.__waiting_count = 0

    def is_waiting(self):
        with self.condition:
            return self.__waiting_count > 0

    def wait(self, condition=lambda var: var is not None, timeout=2):
        with self.condition:
            self.__waiting_count += 1
            try:
                while not condition(self.__var):
                    timed_out = not self.condition.wait(timeout)
                    if timed_out:
                        break
            finally:
                self.__waiting_count -= 1

    def set(self, val):
        with self.condition:
            self.__var = val
            self.condition.notify_all()

    def get(self):
        with self.condition:
            return self.__var

    # https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager
    @contextmanager
    def protecting(self, a, b):
        waited = False
        with self.condition:
            while self.__var == a:
                waited = True
                self.wait(condition=lambda var: var == b)

            # cant call set because inside with
            # cant place outside with because of race conditions
            if not waited:
                self.__var = a
                self.condition.notify_all()

        try:
            yield waited
        finally:
            self.set(b)
