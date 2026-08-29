from vars.consts import TWITCH_OAUTH2_URL

from threading import Thread, Condition
from http.server import HTTPServer, BaseHTTPRequestHandler
import re


class TwitchAuthHandler(BaseHTTPRequestHandler):
    __CODE_RE = re.compile(r"code=([a-z0-9]+)(&|$)")

    def do_GET(self):
        twitch_auth_meta: TwitchAuthMeta = self.server.twitch_auth_meta

        if self.path == "/":
            self.send_response(301)
            self.send_header(
                "Location",
                f"{TWITCH_OAUTH2_URL}/authorize?response_type=code&client_id={twitch_auth_meta.client_id}&redirect_uri={self.server.base_url}&scope=clips:edit",
            )
            self.end_headers()
            return

        if match := re.search(self.__CODE_RE, self.path):
            with twitch_auth_meta.condition:
                twitch_auth_meta.access_token = match.group(1)
                twitch_auth_meta.condition.notify()


class TwitchAuthMeta:
    def __init__(
        self,
        client_id,
        client_secret,
        access_token=None,
        refresh_token=None,
        expires_in=0,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.condition = Condition()
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in


def get_tokens(twitch_auth_meta: TwitchAuthMeta):
    httpd = HTTPServer(("localhost", 3000), TwitchAuthHandler)
    httpd.twitch_auth_meta = twitch_auth_meta
    httpd.base_url = f"http://{httpd.server_name}:{httpd.server_port}"
    print(httpd.base_url)
    t = Thread(target=lambda: httpd.serve_forever())
    t.start()

    with twitch_auth_meta.condition:
        while not twitch_auth_meta.access_token:
            twitch_auth_meta.condition.wait()

    print("main thread:", twitch_auth_meta.access_token)

    httpd.shutdown()
    t.join()
