from chat.Streamer import Streamer, STREAMERS
from chat.TwitchChatIrc import TwitchChatIRC

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


# streamer = STREAMERS[2].initialize()
streamer = Streamer("Arky").initialize()

twitch_chat_irc = TwitchChatIRC()
with twitch_chat_irc as connection:
    connection.listen(streamer)
