# https://github.com/scmanjarrez/twitch-chat-irc/blob/master/twitch_chat_irc/twitch_chat_irc.py

from vars.Streamer import Streamer

import socket
import re


class TwitchChatIRC:
    __HOST = "irc.chat.twitch.tv"
    __DEFAULT_NICK = "justinfan67420"
    __PORT = 6667
    __PATTERN = re.compile(r":[^ ]+ PRIVMSG [^ ]+ :([^\r\n]*)[\r\n]")
    __CURRENT_CHANNEL = None

    def __init__(self, suppress_print=False):
        self.__NICK = self.__DEFAULT_NICK

        self.suppress_print = suppress_print

        self.__SOCKET = socket.socket()

    def connect_to_socket(self) -> None:
        self.__SOCKET.connect((self.__HOST, self.__PORT))
        if not self.suppress_print:
            print(f"Connected to {self.__HOST} on port {self.__PORT}")

        self.__send_raw(f"NICK {self.__NICK}")

    def close_socket_connection(self) -> None:
        self.__SOCKET.close()
        if not self.suppress_print:
            print("Closed connection")

    # https://stackoverflow.com/questions/3774328/implementing-use-of-with-object-as-f-in-custom-class-in-python

    def __enter__(self):
        self.connect_to_socket()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.close_socket_connection()

    def __send_raw(self, string: str) -> None:
        msg = string + "\r\n"
        sent_on_join = self.__SOCKET.send(msg.encode())
        print("sent_on_join =", sent_on_join, ", len(msg) =", len(msg))

    def __recvall(self, buffer_size: int) -> str:
        data = b""
        while True:
            part = self.__SOCKET.recv(buffer_size)
            data += part
            if len(part) < buffer_size:
                break
        return data.decode()

    def __join_channel(self, channel_name: str) -> None:
        channel_lower = channel_name.lower()

        if self.__CURRENT_CHANNEL != channel_lower:
            self.__send_raw(f"JOIN #{channel_lower}")
            self.__CURRENT_CHANNEL = channel_lower

    def is_default_user(self) -> bool:
        return self.__NICK == self.__DEFAULT_NICK

    def listen(
        self,
        streamer: Streamer,
        timeout=None,
        message_timeout=1.0,
        on_message=lambda msg, streamer: print(f"({streamer.login}): {msg}"),
        buffer_size=4096,
    ) -> None:
        self.__join_channel(streamer.login)
        self.__SOCKET.settimeout(message_timeout)

        if not self.suppress_print:
            print("Begin retrieving messages:")

        time_since_last_message = 0
        try:
            while True:
                try:
                    new_info = self.__recvall(buffer_size)

                    if "PING :tmi.twitch.tv" in new_info:
                        self.__send_raw("PONG :tmi.twitch.tv")

                    msg_search = re.findall(self.__PATTERN, new_info)
                    for msg in msg_search:
                        on_message(msg, streamer)

                except socket.timeout:
                    if timeout is not None:
                        time_since_last_message += message_timeout

                        if time_since_last_message >= timeout:
                            if not self.suppress_print:
                                print(
                                    f"No data received in {timeout} "
                                    f"seconds. Timing out."
                                )
                            break

        except KeyboardInterrupt:
            if not self.suppress_print:
                print("Interrupted by user.")
        except Exception as e:
            if not self.suppress_print:
                print("Unknown Error:", e)
            raise e
