import logging
from typing import Any
from typing import Callable

import requests
from requests import Response


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


class _SessionMixin:
    def request(self, method: str, url: str, *args: Any, **kwargs: Any) -> Response:
        return _wrapper(super().request, method, url, *args, **kwargs)


class Session(_SessionMixin, requests.Session):
    pass
