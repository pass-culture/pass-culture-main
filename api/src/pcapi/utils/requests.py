"""This module is a drop-in replacement for the `requests` package.

Wherever you import the `requests` package, you should instead import
this `pcapi.utils.requests` package. It logs HTTP requests and sets a
default timeout if one is not given.

Usage:

    # import requests  # don't do that, just import this package instead
    from pcapi.utils import requests

    response = requests.get("https://example.com")

    # With metrics enabled:
    response = requests.post(
        "https://api.example.com/book",
        json=payload,
        record_metrics=True,
        metric_name_suffix="external_booking"
    )
"""

import logging
import re
from typing import Any
from typing import Callable

import gql.transport.exceptions
import gql.transport.requests
import requests  # noqa: TID251
import zeep
from requests.adapters import HTTPAdapter  # noqa: TID251
from urllib3.util.retry import Retry

from pcapi.utils.metrics import HttpMetricsContext


# fmt: off
# isort: off
# Allow our code to access `requests` exceptions and models directly
# from this wrapper module.
from requests import Response  # noqa: TID251 F401
from requests import exceptions  # noqa: TID251 F401
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


def _redact_url(url: str | None) -> str | None:
    if not url:
        return url
    fields_to_redact = "|".join(  # Fields used in Particulier API queries
        [
            "recipient",
            "nomNaissance",
            "prenoms%5B%5D",  # prenoms%5B%5D unquoted ⇒ prenoms[]
            "nomUsage",
            "anneeDateNaissance",
            "moisDateNaissance",
            "jourDateNaissance",
            "sexeEtatCivil",
            "codeCogInseePaysNaissance",
            "codeCogInseeCommuneNaissance",
            "annee",
            "mois",
            # Allociné and Cine Digital Service (CDS) want authentication token to appear in GET
            # requests. We don't want to log them.
            # For Allociné, the query param name is 'token'. For CDS, the name is 'api_token'
            "token",
        ]
    )
    return re.sub(f"((?:{fields_to_redact})=)[^&]+", r"\1[REDACTED]", url)


def _wrapper(
    request_send_func: Callable,
    request: requests.PreparedRequest,
    log_info: bool,
    **kwargs: Any,
) -> requests.Response:
    if not kwargs.get("timeout"):
        kwargs["timeout"] = REQUEST_TIMEOUT_IN_SECOND

    try:
        response = request_send_func(request, **kwargs)
    except Exception as exc:
        logger.warning(
            "Call to external service failed with %s",
            exc,
            extra={
                "method": request.method,
                "url": _redact_url(request.url),
            },
        )
        raise exc

    if log_info:
        logger.info(
            "External service called",
            extra={
                "url": _redact_url(response.url),
                "statusCode": response.status_code,
                "duration": response.elapsed.total_seconds(),
            },
        )
    return response


def get(
    url: str,
    disable_synchronous_retry: bool = False,
    log_info: bool = True,
    record_metrics: bool = False,
    metric_name_suffix: str | None = None,
    **kwargs: Any,
) -> requests.Response:
    return request(
        "GET",
        url,
        disable_synchronous_retry=disable_synchronous_retry,
        log_info=log_info,
        record_metrics=record_metrics,
        metric_name_suffix=metric_name_suffix,
        **kwargs,
    )


def post(
    url: str,
    hmac: str | None = None,
    disable_synchronous_retry: bool = False,
    log_info: bool = True,
    record_metrics: bool = False,
    metric_name_suffix: str | None = None,
    **kwargs: Any,
) -> requests.Response:
    if hmac:
        kwargs.setdefault("headers", {}).update({"PassCulture-Signature": hmac})
    return request(
        "POST",
        url,
        disable_synchronous_retry=disable_synchronous_retry,
        log_info=log_info,
        record_metrics=record_metrics,
        metric_name_suffix=metric_name_suffix,
        **kwargs,
    )


def put(
    url: str,
    disable_synchronous_retry: bool = False,
    log_info: bool = True,
    record_metrics: bool = False,
    metric_name_suffix: str | None = None,
    **kwargs: Any,
) -> requests.Response:
    return request(
        "PUT",
        url,
        disable_synchronous_retry=disable_synchronous_retry,
        log_info=log_info,
        record_metrics=record_metrics,
        metric_name_suffix=metric_name_suffix,
        **kwargs,
    )


def delete(
    url: str,
    disable_synchronous_retry: bool = False,
    log_info: bool = True,
    record_metrics: bool = False,
    metric_name_suffix: str | None = None,
    **kwargs: Any,
) -> requests.Response:
    return request(
        "DELETE",
        url,
        disable_synchronous_retry=disable_synchronous_retry,
        log_info=log_info,
        record_metrics=record_metrics,
        metric_name_suffix=metric_name_suffix,
        **kwargs,
    )


def request(
    method: str,
    url: str,
    disable_synchronous_retry: bool = False,
    log_info: bool = True,
    record_metrics: bool = False,
    metric_name_suffix: str | None = None,
    **kwargs: Any,
) -> requests.Response:
    with Session(
        disable_synchronous_retry=disable_synchronous_retry,
        log_info=log_info,
        record_metrics=record_metrics,
        metric_name_suffix=metric_name_suffix,
    ) as session:
        return session.request(method=method, url=url, **kwargs)


class Session(requests.Session):
    def __init__(
        self,
        *args: Any,
        disable_synchronous_retry: bool = False,
        log_info: bool = True,
        record_metrics: bool = False,
        metric_name_suffix: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.log_info = log_info
        if record_metrics and metric_name_suffix is None:
            raise ValueError("metric_name_suffix is required when record_metrics is True")
        self.record_metrics = record_metrics
        self.metric_name_suffix = metric_name_suffix

        if disable_synchronous_retry:
            return

        adapter = HTTPAdapter(max_retries=Retry(total=3))

        self.mount("https://", adapter)
        self.mount("http://", adapter)

    def send(self, request: requests.PreparedRequest, **kwargs: Any) -> requests.Response:
        if self.record_metrics and self.metric_name_suffix is not None:
            metrics_context = HttpMetricsContext(
                name_suffix=self.metric_name_suffix,
                method=request.method or "UNKNOWN",
                url=request.url or "",
            )

            with metrics_context:
                response = _wrapper(super().send, request, self.log_info, **kwargs)
                metrics_context.record_response(response.status_code)
                return response
        else:
            return _wrapper(super().send, request, self.log_info, **kwargs)


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
        self.session: requests.Session | None = None
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
