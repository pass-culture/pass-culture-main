from flask import current_app as app
from flask import redirect
from flask import url_for

from . import utils


@app.errorhandler(utils.UnauthenticatedUserError)
def unauthenticated_user_handler(error: utils.UnauthenticatedUserError) -> utils.BackofficeResponse:
    return redirect(url_for("backoffice_v3_web.home"))
