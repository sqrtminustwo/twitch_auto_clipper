from threading import Lock


class LockedCounter:
    def __init__(self):
        self.__num = 0
        self.__lock = Lock()

    @property
    def num(self):
        with self.__lock:
            return self.__num

    @num.setter
    def num(self, value: int):
        assert isinstance(value, int)
        with self.__lock:
            self.__num = value

    def __iadd__(self, other: int):
        with self.__lock:
            self.__num += other
            return self.__num

    def __lt__(self, other: int):
        assert isinstance(other, int)
        with self.__lock:
            return self.__num < other
