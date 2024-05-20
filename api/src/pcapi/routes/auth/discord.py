from flask import render_template
from flask import request

from pcapi.routes.auth.forms.forms import SigninForm

from . import blueprint


@blueprint.auth_blueprint.route("/discord/signin", methods=["GET"])
def discord_signin() -> str:
    form = SigninForm()
    form.redirect_url.data = request.args.get("redirect_url")
    form.discord_id.data = request.args.get("discord_id")
    return render_template("discord_signin.html", form=form)
