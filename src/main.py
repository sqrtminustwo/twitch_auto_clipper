from auth.TwitchAuthTokens import TOKENS
from chat.Streamer import Streamer
from chat.TwitchChatIrc import TwitchChatIRC
from chat.msg_process import msg_process
from vars.consts import STREAMERS, TWITCH_HELIX_URL

# streamer = Streamer(STREAMERS[0]).initialize()
streamer = Streamer("LosPollosTv").initialize()

twitch_chat_irc = TwitchChatIRC()
with twitch_chat_irc as connection:
    connection.listen(streamer, on_message=msg_process)
