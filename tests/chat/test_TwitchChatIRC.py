from twitch_auto_clipper.chat.TwitchChatIRC import TwitchChatIRC

import unittest
from unittest.mock import call, Mock
import socket as s
import signal
from collections.abc import Callable


class TestTwitchChatIRC(unittest.TestCase):
    def setUp(self) -> None:
        self.original_sigint_handler = signal.getsignal(signal.SIGALRM)

        def timeout_handler(signum, frame):
            raise Exception

        signal.signal(signal.SIGALRM, timeout_handler)

        return super().setUp()

    def tearDown(self) -> None:
        signal.signal(signal.SIGALRM, self.original_sigint_handler)
        return super().tearDown()

    def make_class(self) -> Mock:
        mock_socket = Mock()

        mock_socket.connect = Mock()
        mock_socket.send = Mock()
        mock_socket.close = Mock()

        return TwitchChatIRC(mock_socket)

    def get_socket(self, chat_irc: TwitchChatIRC):
        return chat_irc._TwitchChatIRC__SOCKET

    def assert_connection(self, chat_irc):
        socket = self.get_socket(chat_irc)
        socket.connect.assert_called_once_with(
            (chat_irc._TwitchChatIRC__HOST, chat_irc._TwitchChatIRC__PORT)
        )
        socket.send.assert_called_once_with(b"NICK justinfan67420\r\n")

    def test_connect_to_socket(self):
        chat_irc = self.make_class()
        chat_irc.connect_to_socket()
        self.assert_connection(chat_irc)

    def assert_closing(self, chat_irc):
        self.get_socket(chat_irc).close.assert_called_once()

    def test_close_socket_connection(self):
        chat_irc = self.make_class()
        chat_irc.close_socket_connection()
        self.assert_closing(chat_irc)

    def test_with(self):
        chat_irc = self.make_class()

        with chat_irc:
            self.assert_connection(chat_irc)

        self.assert_connection(chat_irc)

    def test_stop_listen_on_timeout_and_not_live(self):
        chat_irc = self.make_class()

        streamer = Mock()
        streamer.is_live = Mock(return_value=False)

        def sender(_):
            raise s.timeout

        self.get_socket(chat_irc).recv = sender

        signal.alarm(3)
        try:
            with chat_irc as connection:
                connection.listen(streamer)

            streamer.is_live.assert_called_once()
        except Exception:
            self.fail("Infinite loop was not ended on offline timed out streamer.")
        finally:
            signal.alarm(0)

    def make_msg(self, i: int) -> bytes:
        content = f"carzy msg {i}"
        msg = f":name15!name15@name15.tmi.twitch.tv PRIVMSG #streamer :{content}\r\n"

        return msg.encode("utf-8"), content

    def common_listen(
        self, sender: Callable[[int], bytes], asserts: Callable[[Mock], None]
    ):
        chat_irc = self.make_class()
        self.get_socket(chat_irc).recv = sender

        streamer = Mock()
        streamer.is_live = Mock(return_value=False)
        streamer.on_message = Mock()

        try:
            with chat_irc as connection:
                connection.listen(streamer)
            self.fail("Should not stop listening on live streamer.")
        except Exception:
            streamer.is_live.assert_called()
            asserts(streamer)

    def test_listen_single(self):
        i = 0
        msg, content = self.make_msg(i)

        def sender(_):
            nonlocal i
            if i == 0:
                i += 1
                return msg
            raise s.timeout

        def asserts(streamer: Mock):
            streamer.on_message.assert_called_once_with(content)

        self.common_listen(sender, asserts)

    def test_listen_multiple(self):
        i = 0
        contents = []

        def sender(_):
            nonlocal i, contents

            if i < 5:
                i += 1
                msg, content = self.make_msg(i)
                contents.append(content)
                return msg

            if i == 5:
                # double message in one send
                msg1, content1 = self.make_msg(i)
                i += 1
                msg2, content2 = self.make_msg(i)

                contents += [content1, content2]

                return msg1 + msg2

            raise s.timeout

        def asserts(streamer: Mock):
            nonlocal contents
            contents = map(lambda c: call(c), contents)
            streamer.on_message.assert_has_calls(contents)

        self.common_listen(sender, asserts)


if __name__ == "__main__":
    unittest.main()
