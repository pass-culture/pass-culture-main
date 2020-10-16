import traceback
from typing import Any, \
    Callable

import requests
from requests import Response

from pcapi.utils.logger import json_logger

REQUEST_TIMEOUT_IN_SECOND = 10


def _log_call_to_external_service(response: Response, *args: Any, **kwargs: Any) -> Response:
    json_logger.info("External service called", extra={
        'url': response.url,
        'statusCode': response.status_code,
        'duration': response.elapsed.total_seconds(),
    })
    return response


def _wrapper(request_func: Callable, method: str, url: str, **kwargs: Any) -> Response:
    try:
        res = request_func(method=method, url=url, timeout=REQUEST_TIMEOUT_IN_SECOND,
                           hooks={'response': _log_call_to_external_service}, **kwargs)
    except Exception as exc:
        json_logger.error("Call to external service failed", extra={'method': method, 'url': url, 'exception': traceback.extract_stack()})
        raise exc

    return res


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
