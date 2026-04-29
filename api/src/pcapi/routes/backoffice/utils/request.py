from typing import Callable
from urllib.parse import urlparse

from flask import Request
from flask import redirect
from flask import request
from flask import url_for
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.wrappers import Response as WerkzeugResponse

from pcapi.routes.backoffice.utils import response as response_utils


def get_query_params() -> ImmutableMultiDict[str, str]:
    """
    Ignore empty query parameters so that they are considered as missing, not set to an empty string.
    This enables to fallback to the default value in wtforms field.
    request.args is an ImmutableMultiDict
    """
    return ImmutableMultiDict(item for item in request.args.items(multi=True) if item[1])


def is_request_from_htmx() -> bool:
    return request.headers.get("hx-request") == "true" and not request.args.get("redirect", False)


def htmx_or_redirect(
    renderer: Callable, url: str, *, follow_referer: bool = False
) -> response_utils.BackofficeResponse:
    if is_request_from_htmx():
        return renderer()
    return safe_redirect_back(
        request=request,
        default_url=url,
        follow_referer=follow_referer,
    )


def safe_redirect_back(
    request: Request, default_url: str | None = None, *, code: int = 303, follow_referer: bool = True
) -> WerkzeugResponse:
    """
    Ensures that the referrer is from the same host before redirecting.
    """
    if referrer := request.referrer:
        if urlparse(referrer).netloc == request.host:
            return redirect(referrer, code=code)
    if default_url:
        return redirect(default_url, code=code)
    return redirect(url_for("backoffice_web.home"), code=code)
