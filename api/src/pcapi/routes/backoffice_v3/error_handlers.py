from flask import current_app as app
from flask import redirect
from flask import request
from flask import url_for

from pcapi.routes.backoffice_v3.home import REDIRECT_AFTER_LOGIN_COOKIE_NAME

from . import utils


@app.errorhandler(utils.UnauthenticatedUserError)
def unauthenticated_user_handler(error: utils.UnauthenticatedUserError) -> utils.BackofficeResponse:
    query_path = request.path
    if request.query_string:
        query_path += f"?{request.query_string.decode()}"
    response = redirect(url_for("backoffice_v3_web.home"))
    response.set_cookie(
        key=REDIRECT_AFTER_LOGIN_COOKIE_NAME,
        value=query_path,
        max_age=600,
        path=url_for("backoffice_v3_web.home"),
        httponly=True,
        secure=True,
    )
    return response
