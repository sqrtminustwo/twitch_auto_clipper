class WordEntry(str):
    def __new__(self, value):
        obj = str.__new__(self, value)
        obj.became_popular = None
        return obj
