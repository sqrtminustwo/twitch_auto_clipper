from chat.TwitchChatIrc import TwitchChatIRC
from chat.msg_process import msg_process
from vars.emotes import make_emotes_for_twitchname
from vars.consts import STREAMERS

streamer = STREAMERS[0]
make_emotes_for_twitchname(streamer)
bot = TwitchChatIRC()
bot.listen(streamer, on_message=msg_process)
bot.close_connection()
