from flask import render_template
from flask_login import current_user

from . import blueprint


@blueprint.poc_backoffice_web.route("/", methods=["GET"])
def home():  # type: ignore
    return render_template("home.template.html", context={"current_user": current_user})
