from flask import Response
from flask import current_app as app
from flask import request
from flask import url_for

from pcapi.routes.backoffice.home import REDIRECT_AFTER_LOGIN_COOKIE_NAME

from . import utils


@app.errorhandler(utils.UnauthenticatedUserError)
def unauthenticated_user_handler(error: utils.UnauthenticatedUserError) -> utils.BackofficeResponse:
    query_path = request.path
    if request.query_string:
        query_path += f"?{request.query_string.decode()}"
    response = Response(
        response="redirecting",
        status=200 if utils.is_request_from_htmx() else 303,
        headers={"HX-Redirect": url_for("backoffice_web.home"), "Location": url_for("backoffice_web.home")},
    )
    if not utils.is_request_from_htmx():
        response.set_cookie(
            key=REDIRECT_AFTER_LOGIN_COOKIE_NAME,
            value=query_path,
            max_age=600,
            path=url_for("backoffice_web.home"),
            httponly=True,
            secure=True,
        )
    return response
