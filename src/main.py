from auth.TwitchAuthTokens import TwitchAuthTokens
from clipper.clipper import clip_now
from vars.Streamer import Streamer
from chat.TwitchChatIrc import TwitchChatIRC
from chat.msg_process import msg_process
from vars.consts import STREAMERS

from dotenv import load_dotenv
from os import getenv

load_dotenv()

tokens: TwitchAuthTokens = TwitchAuthTokens(
    getenv("client_id"), getenv("client_secret")
)
streamer = Streamer(STREAMERS[1]).initialize(tokens)

# clip_now(streamer, tokens)

twitch_chat_irc = TwitchChatIRC()
with twitch_chat_irc as connection:
    connection.listen(streamer, on_message=msg_process)
