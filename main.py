# https://github.com/scmanjarrez/twitch-chat-irc/blob/master/twitch_chat_irc/twitch_chat_irc.py

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

        self.__SOCKET.connect((self.__HOST, self.__PORT))
        if not self.suppress_print:
            print(f"Connected to {self.__HOST} on port {self.__PORT}")

        self.__send_raw(f"NICK {self.__NICK}")

    def __send_raw(self, string):
        msg = string + "\r\n"
        sent_on_join = self.__SOCKET.send(msg.encode())
        print("sent_on_join =", sent_on_join, ", len(msg) =", len(msg))

    def __recvall(self, buffer_size):
        data = b""
        while True:
            part = self.__SOCKET.recv(buffer_size)
            data += part
            if len(part) < buffer_size:
                break
        return data.decode()

    def __join_channel(self, channel_name):
        channel_lower = channel_name.lower()

        if self.__CURRENT_CHANNEL != channel_lower:
            self.__send_raw(f"JOIN #{channel_lower}")
            self.__CURRENT_CHANNEL = channel_lower

    def is_default_user(self):
        return self.__NICK == self.__DEFAULT_NICK

    def close_connection(self):
        self.__SOCKET.close()
        if not self.suppress_print:
            print("Connection closed")

    def listen(
        self,
        channel_name,
        messages=[],
        timeout=None,
        message_timeout=1.0,
        buffer_size=4096,
    ):
        self.__join_channel(channel_name)
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
                    print(msg_search)

                except socket.timeout:
                    print("socket.timeout")
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

        return messages


bot = TwitchChatIRC()
bot.listen("dmitry_lixxx")
bot.close_connection()
