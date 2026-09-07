from threading import Condition
from contextlib import contextmanager


class ProtectedVarWaitTimeOut(Exception):
    pass


class ProtectedVar:
    def __init__(self, value=None):
        self.__value = value
        self.__condition = Condition()
        self.__waiting_count = 0

    def is_waiting(self):
        with self.__condition:
            return self.__waiting_count > 0

    def wait(self, condition=lambda var: var is not None, timeout=2):
        with self.__condition:
            self.__waiting_count += 1
            try:
                while not condition(self.__value):
                    timed_out = not self.__condition.wait(timeout)
                    if timed_out:
                        raise ProtectedVarWaitTimeOut()
            finally:
                self.__waiting_count -= 1

    @property
    def value(self):
        with self.__condition:
            return self.__value

    @value.setter
    def value(self, value: int):
        with self.__condition:
            self.__value = value
            self.__condition.notify_all()

    # https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager
    @contextmanager
    def protecting(self, a, b):
        waited = False
        with self.__condition:
            while self.__value == a:
                waited = True
                self.wait(condition=lambda var: var == b)

            # cant call set because inside "with"
            # cant place outside "with" because of race conditions
            if not waited:
                self.__value = a
                self.__condition.notify_all()

        try:
            yield waited
        finally:
            self.value = b
