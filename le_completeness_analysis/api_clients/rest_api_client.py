import time
from functools import partialmethod
from typing import Any

import httpx
import pendulum
from pendulum import DateTime

JSONType = None | bool | int | float | str | list[Any] | dict[str, Any]


class RestError(Exception):
    """
    Error from REST API Client.
    """

    def __init__(
        self,
        message: str,
        request: httpx.Request,
        response: httpx.Response | None = None,
    ):
        super().__init__(message)
        self.request: httpx.Request = request
        self.response: httpx.Response | None = response


class RestAPIClient:

    def __init__(self, base_url: str, requests_per_sec_max: int, **session_kwargs):
        self._base_url = base_url
        self._client = httpx.Client()
        self._requests_per_sec_max = requests_per_sec_max
        self._last_request_time: DateTime | None = None

        for key, value in session_kwargs.items():
            setattr(self._client, key, value)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        return self._client.close()

    def _throttler(self):
        """
        This method throttles API request based on when the last request was made and the number of maximum number of requests per second configured.
        (the actual frequency of requests can be lower than the maximum allowed if requests take longer to complete than the minimum interval
        between requests)
        """
        if self._last_request_time is None:
            return
        time_since_last_request = self._last_request_time.diff().in_seconds()
        wait_duration = max(0, 1 / self._requests_per_sec_max - time_since_last_request)
        if wait_duration > 0:
            time.sleep(wait_duration)

    def request(self, method: str, path: str, **kwargs) -> tuple[JSONType, RestError]:
        self._throttler()
        try:
            resp = self._client.request(method, f"{self._base_url}/{path}", **kwargs)
            resp.raise_for_status()
            if len(resp.text) == 0:
                return None, None
            return (resp.json(), None)
        except httpx.HTTPStatusError as http_error:
            error_message = http_error.response.json().get("message", "")
            error = RestError(
                f"Error response {http_error.response.status_code} while requesting {http_error.request.url!r}: {error_message}",
                http_error.request,
                http_error.response,
            )
            return (None, error)
        except httpx.RequestError as err:
            error = RestError(
                f"An error occurred while requesting {err.request.url!r}.", err.request
            )
            return (None, error)
        finally:
            self._last_request_time = pendulum.now()

    get = partialmethod(request, "GET")
    post = partialmethod(request, "POST")
    put = partialmethod(request, "PUT")
    patch = partialmethod(request, "PATCH")
    delete = partialmethod(request, "DELETE")
    head = partialmethod(request, "HEAD")
    options = partialmethod(request, "OPTIONS")
