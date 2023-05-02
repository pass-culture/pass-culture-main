from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from werkzeug.exceptions import NotFound

from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
import pcapi.core.users.generator as users_generator
from pcapi.routes.backoffice_v3 import blueprint
from pcapi.routes.backoffice_v3 import utils

from . import forms


@blueprint.backoffice_v3_web.route("/admin/user-generator", methods=["GET"])
@utils.custom_login_required(redirect_to=".home")
def get_generated_user() -> utils.BackofficeResponse:
    form = forms.UserGeneratorForm()
    user = _get_user_if_exists(utils.get_query_params().get("userId"))

    return render_template(
        "admin/users_generator.html", user=user, form=form, dst=url_for("backoffice_v3_web.generate_user")
    )


def _get_user_if_exists(user_id: str | None) -> users_models.User | None:
    if user_id is None:
        return None

    return users_models.User.query.get(int(user_id))
