import logging
import re
from typing import Any
from typing import Callable

import gql.transport.exceptions
import gql.transport.requests
import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import zeep


# fmt: off
# isort: off
# Allow our code to access `requests` exceptions directly from this
# wrapper module.
from requests import exceptions  # pylint: disable=unused-import
# isort: on
# fmt: on

logger = logging.getLogger(__name__)

# See also `SENDINBLUE_REQUEST_TIMEOUT` in `pcapi.core.monkeypatches`
REQUEST_TIMEOUT_IN_SECOND = 10


class ExternalAPIException(Exception):
    is_retryable: bool

    def __init__(self, is_retryable: bool, *args: object) -> None:
        self.is_retryable = is_retryable
        super().__init__(*args)


def _redact_url(url: str | bytes) -> str:
    if isinstance(url, bytes):
        return str(url)
    # Cine Digital Service (CDS) wants authentication token to appear in GET
    # requests. We don't want to log them.
    return re.sub("api_token=[^&^$]+", "api_token=[REDACTED]", url)


def _wrapper(
    request_func: Callable,
    method: str | bytes,
    url: str | bytes,
    log_at_warning_level: bool = True,
    **kwargs: Any,
) -> Response:
    timeout = kwargs.pop("timeout", REQUEST_TIMEOUT_IN_SECOND)
    try:
        response = request_func(method=method, url=url, timeout=timeout, **kwargs)
    except Exception as exc:
        if log_at_warning_level:
            logger_method = logger.warning
        else:
            logger_method = logger.info
        logger_method("Call to external service failed with %s", exc, extra={"method": method, "url": _redact_url(url)})
        raise exc

    logger.info(
        "External service called",
        extra={
            "url": _redact_url(response.url),
            "statusCode": response.status_code,
            "duration": response.elapsed.total_seconds(),
        },
    )
    return response


def get(url: str, disable_synchronous_retry: bool = False, **kwargs: Any) -> Response:
    with Session(disable_synchronous_retry=disable_synchronous_retry) as session:
        return session.request(method="GET", url=url, **kwargs)


def post(url: str, disable_synchronous_retry: bool = False, **kwargs: Any) -> Response:
    with Session(disable_synchronous_retry=disable_synchronous_retry) as session:
        return session.request(method="POST", url=url, **kwargs)


def put(url: str, disable_synchronous_retry: bool = False, **kwargs: Any) -> Response:
    with Session(disable_synchronous_retry=disable_synchronous_retry) as session:
        return session.request(method="PUT", url=url, **kwargs)


def delete(url: str, disable_synchronous_retry: bool = False, **kwargs: Any) -> Response:
    with Session(disable_synchronous_retry=disable_synchronous_retry) as session:
        return session.request(method="DELETE", url=url, **kwargs)


class Session(requests.Session):
    def __init__(self, *args: Any, disable_synchronous_retry: bool = False, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        if disable_synchronous_retry:
            return

        adapter = HTTPAdapter(max_retries=Retry(total=3))

        self.mount("https://", adapter)
        self.mount("http://", adapter)

    def request(self, method: str | bytes, url: str | bytes, *args: Any, **kwargs: Any) -> Response:
        return _wrapper(super().request, method, url, *args, **kwargs)


class CustomZeepTransport(zeep.Transport):
    """A Transport class for zeep that uses our wrapper that logs."""

    def __init__(self, *args: Any, **kwargs: Any):
        kwargs.setdefault("session", Session())
        super().__init__(*args, **kwargs)


class CustomGqlTransport(gql.transport.requests.RequestsHTTPTransport):
    def __init__(self, *args: Any, **kwargs: Any):
        # This is needed to make mypy (almost) happy, otherwise it
        # says that `session` has type `None` (because of the
        # constructor of the parent class) and that triggers an error
        # in `connect()` when setting the attribute.
        self.session: requests.Session | None = None  # type: ignore [assignment]
        super().__init__(*args, **kwargs)

    def connect(self) -> None:
        # This is a copy of `RequestsHTTPTransport.connect()` that
        # uses our own custom `Session` class instead of the default
        # `requests.Session`.
        if self.session is None:
            # --- 8-> --- start of change ---
            # self.session = requests.Session()
            self.session = Session()
            # --- 8-> --- end of change ---

            if self.retries > 0:
                adapter = HTTPAdapter(
                    max_retries=Retry(
                        total=self.retries,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504],
                        allowed_methods=None,
                    )
                )
                for prefix in "http://", "https://":
                    self.session.mount(prefix, adapter)
        else:
            raise gql.transport.exceptions.TransportAlreadyConnected("Transport is already connected")
