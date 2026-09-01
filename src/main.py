from chat.Streamer import STREAMERS
from chat.TwitchChatIrc import TwitchChatIRC
from vars.consts import DEBUG_STREAMER

# from threading import Thread
#
#
# def streamer_thread(streamer: Streamer) -> None:
#     streamer.initialize()
#     twitch_chat_irc = TwitchChatIRC()
#     with twitch_chat_irc as connection:
#         connection.listen(streamer)
#
#
# threads = [
#     Thread(target=streamer_thread, args=(streamer,))
#     for streamer in STREAMERS
#     if streamer.is_live()
# ]
# for thread in threads:
#     thread.start()
#
# for thread in threads:
#     thread.join()


streamer = STREAMERS[1].initialize()

twitch_chat_irc = TwitchChatIRC()
with twitch_chat_irc as connection:
    connection.listen(streamer)
