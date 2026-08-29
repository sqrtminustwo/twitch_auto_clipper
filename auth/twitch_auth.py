# https://dev.twitch.tv/docs/authentication/getting-tokens-oidc/#oidc-authorization-code-grant-flow

from vars.consts import CLIENT_ID, CLIENT_SECRET, TWITCH_OAUTH2_URL

from threading import Thread, Condition
from http.server import HTTPServer, BaseHTTPRequestHandler
import re
import requests


class TwitchAuthHandler(BaseHTTPRequestHandler):
    __CODE_RE = re.compile(r"code=([a-z0-9]+)(&|$)")

    def do_GET(self):
        twitch_auth_meta: TwitchAuthTokens = self.server.twitch_auth_meta

        if self.path == "/":
            self.send_response(301)
            self.send_header(
                "Location",
                f"{TWITCH_OAUTH2_URL}/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={self.server.base_url}&scope=clips:edit",
            )
            self.end_headers()
            return

        if match := re.search(self.__CODE_RE, self.path):
            with twitch_auth_meta.condition:
                twitch_auth_meta.code = match.group(1)
                twitch_auth_meta.condition.notify()


class TwitchAuthTokens:
    def __init__(
        self,
        code=None,
        access_token=None,
        refresh_token=None,
        expires_in=0,
    ):
        self.code = code
        self.condition = Condition()
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in

    def __str__(self):
        parts = [
            f"{self.code = }",
            f"{self.access_token = }",
            f"{self.refresh_token = }",
            f"{self.expires_in = }s",
        ]

        total = ""
        for part in parts:
            total += "\n\t" + part

        return "{" + total + "\n}"


def get_tokens() -> TwitchAuthTokens:
    try:
        twitch_auth_meta = TwitchAuthTokens()
        httpd = HTTPServer(("localhost", 3000), TwitchAuthHandler)
        httpd.twitch_auth_meta = twitch_auth_meta
        local_url = f"http://{httpd.server_name}:{httpd.server_port}"
        httpd.base_url = local_url
        print(local_url)

        t = Thread(target=lambda: httpd.serve_forever())
        t.start()

        with twitch_auth_meta.condition:
            while not twitch_auth_meta.code:
                twitch_auth_meta.condition.wait()

        httpd.shutdown()
        t.join()

        response = requests.post(
            f"{TWITCH_OAUTH2_URL}/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": twitch_auth_meta.code,
                "grant_type": "authorization_code",
                "redirect_uri": local_url,
            },
        ).json()

        for name in ["access_token", "refresh_token", "expires_in"]:
            setattr(twitch_auth_meta, name, response[name])

        print(twitch_auth_meta)

    except Exception as e:
        print(f"Failed to get twitch tokens: {e}")
