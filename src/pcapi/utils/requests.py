import logging
from typing import Any
from typing import Callable

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# fmt: off
# isort: off
# pylint: disable=unused-import
# Keep these imports so that our monkey patch of mailjet_rest allows
# its code to use `requests.exception` and get `RequestException`
# from this module.
from requests import RequestException
import requests.exceptions as exceptions
# pylint: enable=unused-import
# isort: on
# fmt: on

from pcapi import settings


logger = logging.getLogger(__name__)

REQUEST_TIMEOUT_IN_SECOND = 10


def _wrapper(request_func: Callable, method: str, url: str, **kwargs: Any) -> Response:
    timeout = kwargs.pop("timeout", REQUEST_TIMEOUT_IN_SECOND)
    try:
        response = request_func(method=method, url=url, timeout=timeout, **kwargs)
    except Exception as exc:
        logger.exception("Call to external service failed with %s", exc, extra={"method": method, "url": url})
        raise exc
    else:
        logger.info(
            "External service called",
            extra={
                "url": response.url,
                "statusCode": response.status_code,
                "duration": response.elapsed.total_seconds(),
            },
        )

    return response


def get(url: str, **kwargs: Any) -> Response:
    with Session() as session:
        return session.request(method="GET", url=url, **kwargs)


def post(url: str, **kwargs: Any) -> Response:
    with Session() as session:
        return session.request(method="POST", url=url, **kwargs)


def put(url: str, **kwargs: Any) -> Response:
    with Session() as session:
        return session.request(method="PUT", url=url, **kwargs)


def delete(url: str, **kwargs: Any) -> Response:
    with Session() as session:
        return session.request(method="DELETE", url=url, **kwargs)


class _SessionMixin:
    def request(self, method: str, url: str, *args: Any, **kwargs: Any) -> Response:
        return _wrapper(super().request, method, url, *args, **kwargs)


class Session(_SessionMixin, requests.Session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only sets a retry strategy for safe verbs
        safe_retry_strategy = Retry(total=3, method_whitelist=["HEAD", "GET", "OPTIONS"])
        unsafe_retry_strategy = Retry(total=3)
        safe_adapter = HTTPAdapter(max_retries=safe_retry_strategy)
        unsafe_adapter = HTTPAdapter(max_retries=unsafe_retry_strategy)
        self.mount("https://www.demarches-simplifiees.fr", safe_adapter)
        self.mount(settings.JOUVE_API_DOMAIN, safe_adapter)
        self.mount("https://api.mailjet.com", unsafe_adapter)
