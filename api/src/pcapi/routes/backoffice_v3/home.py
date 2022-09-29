from flask import render_template
from flask import url_for
from flask_login import current_user
import werkzeug

from . import blueprint


@blueprint.backoffice_v3_web.route("/", methods=["GET"])
def home():  # type: ignore
    if current_user and not current_user.is_anonymous:
        return werkzeug.utils.redirect(url_for("backoffice_v3_web.search_public_accounts"))
    return render_template("home/login.html")
