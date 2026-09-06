from twitch_auto_clipper.TwitchAutoClipper import TwitchAutoClipper

import unittest
from unittest.mock import Mock, patch, ANY, call


class TestTwitchAutoClipper(unittest.TestCase):
    names = ["streamer1", "streamer2"]
    client_id = "client_id"
    client_secret = "client_secret"

    def setUp(self):
        self.mock_streamer = patch(
            "twitch_auto_clipper.TwitchAutoClipper.Streamer"
        ).start()
        self.mock_tokens = patch(
            "twitch_auto_clipper.TwitchAutoClipper.TwitchAuthTokens"
        ).start()

        self.tokens = Mock()
        self.tokens.initialize = Mock()
        self.mock_tokens.side_effect = [self.tokens]

        self.streamers = [Mock(), Mock()]
        self.mock_streamer.side_effect = self.streamers

        self.clipper = TwitchAutoClipper(
            self.names,
            self.client_id,
            self.client_secret,
            on_clip=lambda _: None,
        )

    def tearDown(self):
        patch.stopall()

    def test_init(self):
        self.mock_tokens.assert_called_once_with(self.client_id, self.client_secret)
        self.tokens.initialize.assert_called_once()
        self.mock_streamer.assert_has_calls([call(name, ANY) for name in self.names])

    def make_start(self):
        twitch_char_irc_mock = patch(
            "twitch_auto_clipper.TwitchAutoClipper.TwitchChatIRC"
        ).start()

        self.chat_mocks = []
        self.connection_mocks = [Mock(), Mock()]
        for i in range(2):
            twitch_char_irc = Mock()
            twitch_char_irc.__enter__ = Mock(return_value=self.connection_mocks[i])
            twitch_char_irc.__exit__ = Mock()
            twitch_char_irc.listen = Mock()
            self.chat_mocks.append(twitch_char_irc)

        self.streamers[0].is_live = Mock(return_value=False)
        self.streamers[1].is_live = Mock(return_value=True)

        twitch_char_irc_mock.side_effect = self.chat_mocks

    def test_start(self):
        self.make_start()

        self.clipper.start()
        self.clipper.join()

        chat = self.chat_mocks[0]
        chat.__enter__.assert_called_once()
        chat.__exit__.assert_called_once()
        self.connection_mocks[0].listen.assert_called_once()

    def make_join(self):
        self.make_start()

        thread = Mock()
        thread.join = Mock()
        self.clipper._TwitchAutoClipper__threads = [thread]

        return thread

    def test_join(self):
        thread = self.make_join()

        i = 0

        def raise_join():
            nonlocal i
            if i > 0:
                return
            i += 1
            raise KeyboardInterrupt()

        thread.join = raise_join

        self.clipper._TwitchAutoClipper__threads = [thread]

        for streamer in self.clipper._TwitchAutoClipper__streamers:
            streamer.stop_listening = Mock()
            streamer.stop_listening.value = False

        self.clipper.join()

        for streamer in self.streamers:
            self.assertTrue(streamer.stop_listening.value)


if __name__ == "__main__":
    unittest.main()
