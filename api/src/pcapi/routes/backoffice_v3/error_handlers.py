from base64 import b64encode

from flask import current_app as app
from flask import redirect
from flask import request
from flask import url_for

from . import utils


@app.errorhandler(utils.UnauthenticatedUserError)
def unauthenticated_user_handler(error: utils.UnauthenticatedUserError) -> utils.BackofficeResponse:
    query_path = request.path
    if request.query_string:
        query_path += f"?{request.query_string.decode()}"
    return redirect(url_for("backoffice_v3_web.home", redirect=b64encode(query_path.encode())))
