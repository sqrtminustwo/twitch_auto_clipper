from twitch_auto_clipper.clip.Clip import Clip
from twitch_auto_clipper.chat.Message import Message

from tests.helpers import now_minus_delta
from datetime import datetime
import unittest


class TestClip(unittest.TestCase):
    def make_class(self, message=None, ratio=0):
        return Clip(message=message, broadcaster_id="123", message_count=0, ratio=ratio)

    def test_set_timestamp_bound(self):
        message = Message("msg")
        message.became_popular = now_minus_delta(5)

        clip = self.make_class(message)
        clip.set_timestamp(datetime.now())

        self.assertGreater(clip.timestamp, 0)
        self.assertLess(clip.timestamp, Clip.MAX_CLIP_LENGTH)

    def test_lt(self):
        self.assertGreater(self.make_class(ratio=0.5), self.make_class(ratio=0))
        self.assertLess(self.make_class(ratio=0.2), self.make_class(ratio=0.8))


if __name__ == "__main__":
    unittest.main()
