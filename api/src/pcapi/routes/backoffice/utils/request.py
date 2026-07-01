from typing import Callable
from urllib.parse import urlparse

from flask import Request
from flask import current_app as app
from flask import redirect
from flask import request
from flask import url_for
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import HTTPException
from werkzeug.routing.exceptions import RequestRedirect
from werkzeug.routing.rules import Rule
from werkzeug.wrappers import Response as WerkzeugResponse

from pcapi import settings

from .response import BackofficeResponse


def get_query_params() -> ImmutableMultiDict[str, str]:
    """
    Ignore empty query parameters so that they are considered as missing, not set to an empty string.
    This enables to fallback to the default value in wtforms field.
    request.args is an ImmutableMultiDict
    """
    return ImmutableMultiDict(item for item in request.args.items(multi=True) if item[1])


def is_request_from_htmx() -> bool:
    return request.headers.get("hx-request") == "true" and not request.args.get("redirect", False)


def redirect_if_not_htmx(route: str, render_function: Callable) -> BackofficeResponse:
    if is_request_from_htmx():
        return render_function()
    return redirect(route, code=303)


def safe_redirect_back(request: Request, default_url: str | None = None, *, code: int = 303) -> WerkzeugResponse:
    """
    Ensures that the referrer is from the same host before redirecting.
    """
    if referrer := request.referrer:
        if urlparse(referrer).netloc == request.host:
            return redirect(referrer, code=code)
    if default_url:
        return redirect(default_url, code=code)
    return redirect(url_for("backoffice_web.home"), code=code)


# Derived from https://stackoverflow.com/questions/19631335/reverting-a-url-in-flask-to-the-endpoint-arguments
def rule_for_url(url: str, method: str = "GET") -> Rule | None:
    """
    Given an absolute URL, retrieve the matching endpoint name (or rule).
    Requires a current request context to determine runtime environment.

    :param str method: HTTP method to use (defaults to GET)
    :return: Endpoint name or URL rule, or `None` if not found
    """
    parsed_url = urlparse(url)
    if not parsed_url.netloc:
        # We require an absolute URL
        return None
    if not parsed_url.netloc == urlparse(settings.BACKOFFICE_URL).netloc:
        # only accept URL from BO
        return None

    # Take the current runtime environment...
    environ = dict(request.environ)
    # ...but replace the HTTP host with the URL's host...
    environ["HTTP_HOST"] = parsed_url.netloc
    # ...and the path with the URL's path (after discounting the app path, if not hosted at root).
    environ["PATH_INFO"] = parsed_url.path[len(environ["SCRIPT_NAME"]) :]
    # Create a new request with this environment...
    url_request = app.request_class(environ)
    # ...and a URL adapter with the new request.
    url_adapter = app.create_url_adapter(url_request)

    assert url_adapter is not None  # helps mypy

    try:
        rule, view_args = url_adapter.match(parsed_url.path, method, return_rule=True)
        return rule
    except RequestRedirect as r:
        # A redirect typically implies `/folder` -> `/folder/`
        # This will not be a redirect response from a view, since the view isn't being called
        return rule_for_url(r.new_url, method=method)
    except HTTPException:
        pass
    # If we got here, no endpoint was found.
    return None
