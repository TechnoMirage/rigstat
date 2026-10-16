import json
import urllib.error
import urllib.request
from typing import Any, Optional

try:
    from exceptions import ApiAuthError, ApiConnectionError, ApiError
except ImportError:
    from ..exceptions import ApiAuthError, ApiConnectionError, ApiError


class XMRigApi:
    def __init__(
        self,
        ip: str,
        port: int,
        access_token: Optional[str] = None,
        timeout: float = 10.0,
    ) -> None:
        self.ip = ip
        self.port = port
        self.access_token = access_token
        self.timeout = timeout

    @property
    def base_url(self) -> str:
        return f"http://{self.ip}:{self.port}/2"

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "rigstat-xmrig-client/1.0",
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def get_summary(self) -> dict[str, Any]:
        url = f"{self.base_url}/summary"
        req = urllib.request.Request(url, headers=self._get_headers(), method="GET")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw_data = response.read().decode("utf-8")
                return json.loads(raw_data)

        except urllib.error.HTTPError as err:
            error_body = ""
            try:
                error_body = err.read().decode("utf-8")
            except Exception:
                pass
            finally:
                err.close()

            message = (
                f"[xmrig] HTTP {err.code} ({err.reason}) for {url}. Error: {error_body}"
            )
            if err.code in (401, 403):
                raise ApiAuthError(message) from err
            raise ApiError(message) from err

        except (urllib.error.URLError, TimeoutError) as err:
            raise ApiConnectionError(
                f"[xmrig] Cant connection to {url}. Error: {err}"
            ) from err

        except json.JSONDecodeError as err:
            raise ApiError(
                f"[xmrig] Response from {url} is not valid. Error: {err}"
            ) from err