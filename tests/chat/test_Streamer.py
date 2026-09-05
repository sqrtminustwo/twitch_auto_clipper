from twitch_auto_clipper_sqrtminusone.chat.Streamer import Streamer
from twitch_auto_clipper_sqrtminusone.clip.Clip import Clip
from twitch_auto_clipper_sqrtminusone.utils.utils import now

import unittest
from unittest.mock import Mock, ANY
import datetime


class TestStreamer(unittest.TestCase):
    id = "streamer_id"
    login = "streamer"

    def set_get_return(self, context, obj={}):
        context.tokens.authorized_get_json = Mock(return_value=obj)

    def make_class(self, requests=Mock()) -> Mock:
        context = Mock()
        context.tokens = Mock()
        self.set_get_return(context, {"data": [{"id": self.id}]})
        context.clipable_wait = 0
        context.common_value = 1
        context.emote_value = 2
        streamer = None

        try:
            streamer = Streamer(self.login, context, requests=requests)
        except Exception:
            self.fail("Can't fail initialization, seventv emotes are optional.")

        return streamer

    def test_initialize_no_seventv(self):
        streamer = self.make_class()

        streamer.context.tokens.authorized_get_json.assert_called_once_with(
            ANY, params={"login": streamer.login}
        )
        self.assertEqual(streamer.id, self.id)

    def test_initialize_with_seventv(self):
        requests = Mock()
        response = Mock()

        emote_names = ["LOL", "kappa", "SON"]
        emotes = [{"name": name} for name in emote_names]

        response.json = Mock(return_value={"emote_set": {"emotes": emotes}})
        requests.get = Mock(return_value=response)
        streamer = self.make_class(requests)

        requests.get.assert_called_once()
        self.assertTrue(self.id in requests.get.call_args[0][0])
        self.assertEqual(
            streamer.seventv_emotes, {name.lower() for name in emote_names}
        )

    def live_common(self, data) -> Mock:
        streamer = self.make_class()
        self.set_get_return(streamer.context, {"data": data})
        return streamer

    def test_is_live(self):
        self.assertTrue(self.live_common([self.id]).is_live())

    def test_is_not_live(self):
        self.assertFalse(self.live_common([]).is_live())

    def test_clip(self):
        streamer = self.make_class()

        url = "url123123"
        streamer.context.tokens.authorized_post_json = Mock(
            return_value={"data": [{"edit_url": url}]}
        )
        streamer.context.on_clip = Mock()

        clip = Mock()
        clip.broadcaster_id = self.id

        streamer.clip(clip)

        self.assertEqual(clip.url, url)
        streamer.context.on_clip.assert_called_once_with(clip)

    def test_message_value(self):
        streamer = self.make_class()
        streamer.seventv_emotes = {"lol"}

        c = streamer.context.common_value
        e = streamer.context.emote_value

        for msg, expected in [("a", c), ("lol", e), ("Lol", e)]:
            self.assertEqual(streamer.get_message_value(msg), expected)

    def make_for_on_message(self):
        streamer = self.make_class()
        streamer.context.excluded_words = {}
        streamer.context.clipable_message_ratio = 0.5

        return streamer

    def test_most_used(self):
        streamer = self.make_for_on_message()
        streamer.start_of_snapshot = now()
        streamer.context.counter_interval_seconds = 1000

        streamer.on_message("lol lol lol")
        m, c = streamer.most_used
        self.assertEqual(m, "lol")
        self.assertEqual(c, 1)

        streamer.seventv_emotes = {"123"}

        streamer.on_message("123")
        streamer.on_message("123")
        streamer.on_message("123 321")
        m, c = streamer.most_used
        self.assertEqual(m, "123")
        self.assertEqual(c, 6)

    def test_on_message_doesnt_clip_interval(self):
        streamer = self.make_for_on_message()
        streamer.start_of_snapshot = now()
        streamer.context.counter_interval_seconds = 10
        streamer.clip = Mock()

        # 2 times to join the last thread if it clips
        streamer.on_message("a")
        streamer.on_message("b")

        streamer.clip.assert_not_called()

    def make_with_interval(self):
        streamer = self.make_for_on_message()
        streamer.context.counter_interval_seconds = 10
        streamer.clip = Mock()

        return streamer

    def set_not_in_inverval(self, streamer):
        streamer.start_of_snapshot = now()

    def set_in_inverval(self, streamer):
        streamer.start_of_snapshot = now() - datetime.timedelta(seconds=12)

    def test_on_message_doesnt_clip_not_popular(self):
        streamer = self.make_with_interval()

        self.set_not_in_inverval(streamer)
        streamer.on_message("a")
        streamer.on_message("b")

        self.set_in_inverval(streamer)
        streamer.on_message("c")

        self.assertIsNone(streamer.clipping_thread)
        streamer.clip.assert_not_called()

    def test_on_message_clips_popular(self):
        streamer = self.make_with_interval()

        self.set_not_in_inverval(streamer)
        streamer.on_message("a")
        self.set_in_inverval(streamer)
        streamer.on_message("b")

        if streamer.clipping_thread is not None:
            streamer.clipping_thread.join()
        streamer.clip.assert_called_once_with(
            Clip(broadcaster_id=self.id, message="b", emote_count=1, ratio=0.5)
        )


if __name__ == "__main__":
    unittest.main()
