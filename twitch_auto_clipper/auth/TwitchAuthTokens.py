# https://dev.twitch.tv/docs/authentication/getting-tokens-oidc/#oidc-authorization-code-grant-flow

from ApiUrls import ApiUrls
from utils.ProtectedVar import ProtectedVar

from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import re
import requests
import logging
import webbrowser


class TwitchAuthHandler(BaseHTTPRequestHandler):
    __CODE_RE = re.compile(r"code=([a-z0-9]+)(&|$)")

    def do_GET(self):
        code: ProtectedVar = self.server.code
        client_id: str = self.server.client_id

        if self.path == "/":
            self.send_response(301)
            self.send_header(
                "Location",
                f"{ApiUrls.TWITCH_OAUTH2_URL}/authorize?response_type=code&client_id={client_id}&redirect_uri={self.server.base_url}&scope=clips:edit",
            )
            self.end_headers()
            return

        if match := re.search(self.__CODE_RE, self.path):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.wfile.write(
                "Authentication is done, you can close this tab.".encode("utf-8")
            )
            code.set(match.group(1))
            return


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

        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__code = code

        self.__refresh_protector = ProtectedVar(False)
        self.__access_token = access_token
        self.__refresh_token = refresh_token
        self.expires_in = expires_in

        self.__initialize()

    def __repr__(self):
        parts = [
            f"client_id = {self.__client_id}"
            f"client_secret = {self.__client_secret}"
            f"code = {self.__code}",
            f"access_token = {self.__access_token}",
            f"refresh_token = {self.__refresh_token}",
            f"expires_in = {self.expires_in = }",
        ]

        total = ""
        for part in parts:
            total += "\n\t" + part

        return f"{self.__class__.__name__}(" + total + "\n)"

    def __authorized_method_json(
        self, method, url, params, ok_code, recursive=False
    ) -> requests.Response:
        try:
            response = method(
                url,
                headers={
                    "Authorization": f"Bearer {self.__access_token}",
                    "Client-Id": self.__client_id,
                },
                params=params,
            )

            if response.status_code == ok_code:
                return response.json()

            if response.status_code == 401:
                if recursive:
                    raise Exception("Refresh failed")
                self.__refresh()
                return self.__authorized_method_json(
                    self, method, url, params, recursive=True
                )

            response.raise_for_status()
        except Exception as e:
            logging.error(f"Failed authorized_get for {url}: {e}")

    def authorized_get_json(self, url, params={}):
        return self.__authorized_method_json(requests.get, url, params, 200)

    def authorized_post(self, url, params, ok_code) -> requests.Response:
        return self.__authorized_method_json(requests.post, url, params, ok_code)

    def __request_tokens_and_set(self, data) -> None:
        data["client_id"] = self.__client_id
        data["client_secret"] = self.__client_secret

        response = requests.post(f"{ApiUrls.TWITCH_OAUTH2_URL}/token", data)
        response.raise_for_status()
        response = response.json()

        self.__access_token = response["access_token"]
        self.__refresh_token = response["refresh_token"]
        self.expires_in = response["expires_in"]

        logging.debug(self)

    def __refresh(self) -> None:
        with self.__refresh_protector.protecting(True, False) as protecting:
            # Already refreshing
            if protecting:
                return

            try:
                self.__request_tokens_and_set(
                    {
                        "grant_type": "refresh_token",
                        "refresh_token": self.__refresh_token,
                    }
                )
            except Exception as e:
                logging.error(f"Failed to refresh tokens: {e}")

    def __initialize(self) -> None:
        try:
            httpd = HTTPServer(("localhost", 3000), TwitchAuthHandler)

            code: ProtectedVar = ProtectedVar()
            httpd.code = code
            httpd.client_id = self.__client_id

            local_url = f"http://{httpd.server_name}:{httpd.server_port}"
            httpd.base_url = local_url
            webbrowser.open(local_url)

            t = Thread(target=lambda: httpd.serve_forever())
            t.start()

            code.wait()

            httpd.shutdown()
            t.join()

            self.__code = code.get()

            self.__request_tokens_and_set(
                {
                    "grant_type": "authorization_code",
                    "code": self.__code,
                    "redirect_uri": local_url,
                }
            )

            return self
        except Exception as e:
            logging.critical(f"Failed to initialize twitch tokens: {e}")
