from flask import render_template
from flask_login import current_user

from . import blueprint
from . import utils


@blueprint.backoffice_v3_web.route("/", methods=["GET"])
def home() -> utils.BackofficeResponse:
    if current_user and not current_user.is_anonymous:
        return render_template("home/home.html")
    return render_template("home/login.html")
