from typing import Any, Callable

import requests
from requests import Response

from pcapi.utils.logger import json_logger

REQUEST_TIMEOUT_IN_SECOND = 10


def _wrapper(request_func: Callable, method: str, url: str, **kwargs: Any) -> Response:
    try:
        response = request_func(method=method, url=url, timeout=REQUEST_TIMEOUT_IN_SECOND, **kwargs)
        json_logger.info("External service called", extra={
            'url': response.url,
            'statusCode': response.status_code,
            'duration': response.elapsed.total_seconds(),
        })
    except Exception as exc:
        json_logger.exception("Call to external service failed with %s", exc, extra={'method': method, 'url': url})
        raise exc

    return response


def get(url: str, **kwargs: Any) -> Response:
    with Session() as session:
        return session.request(
            method='GET',
            url=url,
            **kwargs
        )


def post(url: str, **kwargs: Any) -> Response:
    with Session() as session:
        return session.request(
            method='POST',
            url=url,
            **kwargs
        )


class _SessionMixin:
    def request(
            self,
            method: str,
            url: str,
            *args: Any,
            **kwargs: Any
    ) -> Response:
        return _wrapper(
            super().request,
            method,
            url,
            *args,
            **kwargs
        )


class Session(_SessionMixin, requests.Session):
    pass
