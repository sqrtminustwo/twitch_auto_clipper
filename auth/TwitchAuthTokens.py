# https://dev.twitch.tv/docs/authentication/getting-tokens-oidc/#oidc-authorization-code-grant-flow

from vars.consts import TWITCH_OAUTH2_URL
from utils.utils import ProtectedVar

from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import re
import requests


class TwitchAuthHandler(BaseHTTPRequestHandler):
    __CODE_RE = re.compile(r"code=([a-z0-9]+)(&|$)")

    def do_GET(self):
        code: ProtectedVar = self.server.code
        client_id: str = self.server.client_id

        if self.path == "/":
            self.send_response(301)
            self.send_header(
                "Location",
                f"{TWITCH_OAUTH2_URL}/authorize?response_type=code&client_id={client_id}&redirect_uri={self.server.base_url}&scope=clips:edit",
            )
            self.end_headers()
            return

        if match := re.search(self.__CODE_RE, self.path):
            code.set(match.group(1))


class TwitchAuthTokens:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        code=None,
        access_token=None,
        refresh_token=None,
        expires_in=0,
    ):
        for var in [client_id, client_secret]:
            assert type(var) is str and len(var) > 0

        self.client_id = client_id
        self.client_secret = client_secret
        self.code = code

        self.refresh_protector = ProtectedVar(False)
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

    def __request_tokens_and_set(self, data) -> None:
        data["client_id"] = self.client_id
        data["client_secret"] = self.client_secret

        response = requests.post(f"{TWITCH_OAUTH2_URL}/token", data).json()

        for name in ["access_token", "refresh_token", "expires_in"]:
            setattr(self, name, response[name])

        print(self)

    def refresh_tokens(self) -> None:
        with self.refresh_protector.protecting(True, False) as protecting:
            # Already refreshing
            if protecting:
                return

            self.__request_tokens_and_set(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                }
            )

    def initialize_tokens(self) -> None:
        try:
            httpd = HTTPServer(("localhost", 3000), TwitchAuthHandler)

            code: ProtectedVar = ProtectedVar()
            httpd.code = code
            httpd.client_id = self.client_id

            local_url = f"http://{httpd.server_name}:{httpd.server_port}"
            httpd.base_url = local_url
            print(local_url)

            t = Thread(target=lambda: httpd.serve_forever())
            t.start()

            code.wait_conditional_on_var()

            httpd.shutdown()
            t.join()

            self.code = code.get()

            self.__request_tokens_and_set(
                {
                    "grant_type": "authorization_code",
                    "code": self.code,
                    "redirect_uri": local_url,
                }
            )
        except Exception as e:
            print(f"Failed to get twitch tokens: {e}")
