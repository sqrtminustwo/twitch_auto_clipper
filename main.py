from auth.twitch_auth import TwitchAuthMeta, get_tokens
from dotenv import load_dotenv  # type: ignore
from os import getenv

# from chat.TwitchChatIrc import TwitchChatIRC
# from chat.msg_process import msg_process
# from vars.emotes import make_emotes_for_twitchname
# from vars.consts import STREAMERS
#
# streamer = STREAMERS[0]
# make_emotes_for_twitchname(streamer)
# bot = TwitchChatIRC()
# bot.listen(streamer, on_message=msg_process)
# bot.close_connection()

load_dotenv()
print(getenv("client_id"), getenv("client_secret"))
twitch_auth_meta = TwitchAuthMeta(getenv("client_id"), getenv("client_secret"))
get_tokens(twitch_auth_meta)
