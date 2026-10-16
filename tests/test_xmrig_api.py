import io
import json
import os
import sys
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from exceptions import ApiAuthError, ApiConnectionError, ApiError, RigStatError
from monero.xmrig_api import XMRigApi


class TestXMRigApi(unittest.TestCase):

    TEST_IP = "127.0.0.1"
    TEST_PORT = 16000
    TEST_TOKEN = "test-token"

    def setUp(self):
        self.api = XMRigApi(
            ip=self.TEST_IP,
            port=self.TEST_PORT,
            access_token=self.TEST_TOKEN,
            timeout=5.0,
        )

    def test_base_url_formatting(self):
        self.assertEqual(self.api.base_url, f"http://{self.TEST_IP}:{self.TEST_PORT}/2")

    @patch("urllib.request.urlopen")
    def test_get_summary_success_with_token(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "version": "6.21.0",
            "hashrate": {"total": [1200.5]}
        }).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        data = self.api.get_summary()

        self.assertEqual(data["version"], "6.21.0")
        self.assertEqual(data["hashrate"]["total"], [1200.5])

        # Vérification des arguments passés à urlopen
        called_req = mock_urlopen.call_args[0][0]
        called_kwargs = mock_urlopen.call_args[1]
        self.assertEqual(called_req.full_url, f"http://{self.TEST_IP}:{self.TEST_PORT}/2/summary")
        self.assertEqual(called_req.headers["Authorization"], f"Bearer {self.TEST_TOKEN}")
        self.assertEqual(called_kwargs.get("timeout"), 5.0)

    @patch("urllib.request.urlopen")
    def test_get_summary_without_token(self, mock_urlopen):
        client_no_token = XMRigApi(ip=self.TEST_IP, port=self.TEST_PORT, access_token=None)

        mock_response = MagicMock()
        mock_response.read.return_value = b"{}"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        client_no_token.get_summary()

        called_req = mock_urlopen.call_args[0][0]
        self.assertNotIn("Authorization", called_req.headers)

    @patch("urllib.request.urlopen")
    def test_connection_error_on_urlerror(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        with self.assertRaises(ApiConnectionError) as ctx:
            self.api.get_summary()
        self.assertIn("Cant connection to", str(ctx.exception))

    @patch("urllib.request.urlopen")
    def test_connection_error_on_timeout(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError("Request timed out")

        with self.assertRaises(ApiConnectionError):
            self.api.get_summary()

    @patch("urllib.request.urlopen")
    def test_auth_error_on_401(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url=f"http://{self.TEST_IP}:{self.TEST_PORT}/2/summary",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=io.BytesIO(b"Invalid token"),
        )

        with self.assertRaises(ApiAuthError) as ctx:
            self.api.get_summary()
        self.assertIn("Invalid token", str(ctx.exception))

    @patch("urllib.request.urlopen")
    def test_auth_error_on_403(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url=f"http://{self.TEST_IP}:{self.TEST_PORT}/2/summary",
            code=403,
            msg="Forbidden",
            hdrs={},
            fp=io.BytesIO(b"IP restricted"),
        )

        with self.assertRaises(ApiAuthError):
            self.api.get_summary()

    @patch("urllib.request.urlopen")
    def test_generic_http_error_on_500(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url=f"http://{self.TEST_IP}:{self.TEST_PORT}/2/summary",
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=io.BytesIO(b"Crash"),
        )

        with self.assertRaises(ApiError):
            self.api.get_summary()

    @patch("urllib.request.urlopen")
    def test_json_decode_error(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>Server Error</html>"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        with self.assertRaises(ApiError):
            self.api.get_summary()

    def test_exception_inheritance(self):
        self.assertTrue(issubclass(ApiConnectionError, ApiError))
        self.assertTrue(issubclass(ApiAuthError, ApiError))
        self.assertTrue(issubclass(ApiError, RigStatError))


if __name__ == "__main__":
    unittest.main()
