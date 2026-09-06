from twitch_auto_clipper.utils.utils import now_formated

import datetime
import unittest
from unittest.mock import Mock


class TestUtils(unittest.TestCase):
    def test_now_fromated(self):
        d = Mock()
        d.now = Mock(return_value=datetime.datetime(2026, 9, 5, 22, 36, 20))
        self.assertEqual(now_formated(datetime=d), "05-09-2026_22:36:20")


if __name__ == "__main__":
    unittest.main()
