import requests
from twitch_auto_clipper.auth.TwitchAuthTokens import TwitchAuthTokens
from twitch_auto_clipper.utils.ProtectedVar import ProtectedVar
from twitch_auto_clipper.Urls import Urls

from helpers import for_testing_protected, id, join_all
import unittest
from unittest.mock import Mock, ANY, patch
from threading import Thread


class TestTwitchAuthTokens(unittest.TestCase):
    fake_data = {"a": 1, "b": 2}

    def test_request_tokens_and_set(self):
        client_id = "client_id"
        client_secret = "client_secret"

        response_mock = Mock()
        response_mock.raise_for_status = Mock()
        response_json = {
            "access_token": "123",
            "refresh_token": "345",
            "expires_in": "5",
        }
        response_mock.json = Mock(return_value=response_json)

        requests_mock = Mock()
        requests_mock.post = Mock(return_value=response_mock)

        tokens = TwitchAuthTokens(
            client_id=client_id, client_secret=client_secret, requests=requests_mock
        )

        data = self.fake_data.copy()
        tokens._TwitchAuthTokens__request_tokens_and_set(data)

        data["client_id"] = client_id
        data["client_secret"] = client_secret
        requests_mock.post.assert_called_once_with(ANY, data)

        self.assertEqual(
            response_json,
            {
                "access_token": tokens._TwitchAuthTokens__access_token,
                "refresh_token": tokens._TwitchAuthTokens__refresh_token,
                "expires_in": tokens.expires_in,
            },
        )

    def make_class(self, requests_mock: Mock = Mock()) -> TwitchAuthTokens:
        return TwitchAuthTokens("a", "b", requests=requests_mock)

    @patch.object(TwitchAuthTokens, "_TwitchAuthTokens__refresh")
    def test_calls_refresh_on_401(self, refresh_mock):
        respone_mock = Mock()
        respone_mock.status_code = 401

        requests_mock = Mock()
        requests_mock.get = Mock(return_value=respone_mock)

        tokens = self.make_class(requests_mock)
        tokens.authorized_get_json("url")

        self.assertEqual(requests_mock.get.call_count, 2)
        refresh_mock.assert_called_once()

    def authorized_method_json(self, method, mock_name):
        respone_mock = Mock()
        respone_mock.status_code = 200
        respone_mock.json = Mock(return_value=self.fake_data)

        requests_mock = Mock()
        setattr(requests_mock, mock_name, Mock(return_value=respone_mock))

        tokens = self.make_class(requests_mock)
        url = "url"
        params = {"param": 123}
        method(tokens, url, params)

        getattr(requests_mock, mock_name).assert_called_once_with(
            url,
            headers={
                "Authorization": ANY,
                "Client-Id": tokens._TwitchAuthTokens__client_id,
            },
            params=params,
        )

    def test_authorized_get_json(self):
        self.authorized_method_json(
            lambda tokens, url, params: tokens.authorized_get_json(url, params), "get"
        )

    def test_authorized_post_json(self):
        self.authorized_method_json(
            lambda tokens, url, params: tokens.authorized_post_json(url, params, 200),
            "post",
        )

    @patch.object(TwitchAuthTokens, "_TwitchAuthTokens__request_tokens_and_set")
    def test_refresh_multi_thread_protection(self, request_tokens_and_set_mock):
        tokens = self.make_class()

        done = ProtectedVar(False)
        request_tokens_and_set_mock.side_effect = lambda _: done.wait(id)

        refresh_threads = for_testing_protected(
            lambda: tokens._TwitchAuthTokens__refresh(), done
        )
        done.value = True

        join_all(refresh_threads)
        request_tokens_and_set_mock.assert_called_once()

    def test_initialize(self):
        webbrowser = Mock()
        tokens = TwitchAuthTokens("a", "b", webbrowser=webbrowser)
        request_tokens_and_set_mock = Mock()
        tokens._TwitchAuthTokens__request_tokens_and_set = request_tokens_and_set_mock

        initialize_thread = Thread(target=lambda: tokens.initialize())
        initialize_thread.start()

        webserver_live = tokens._TwitchAuthTokens__webserver_live
        webserver_live.wait(id)

        hostname, port = Urls.LOCAL_WEBSERVER
        url = f"http://{hostname}:{port}"

        response = requests.get(url, allow_redirects=False)
        self.assertEqual(response.status_code, 301)
        self.assertTrue(response.headers["location"].startswith(Urls.TWITCH_OAUTH2_URL))

        code = "123"
        requests.get(f"{url}/code={code}")

        initialize_thread.join()

        self.assertEqual(tokens._TwitchAuthTokens__code, code)
        request_tokens_and_set_mock.assert_called_once()

    def test_repr(self):
        tokens = TwitchAuthTokens(
            "a",
            "b",
            code="3",
            access_token="4",
            refresh_token="5",
            expires_in=5,
        )

        try:
            exec(repr(tokens))
        except Exception:
            self.fail("repr can not be used to create class")


if __name__ == "__main__":
    unittest.main()
