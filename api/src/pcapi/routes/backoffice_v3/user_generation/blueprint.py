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


@blueprint.backoffice_v3_web.route("/admin/user-generator", methods=["POST"])
@utils.custom_login_required(redirect_to=".home")
def generate_user() -> utils.BackofficeResponse:
    form = forms.UserGeneratorForm()

    if not form.validate():
        error_msg = utils.build_form_error_msg(form)
        flash(error_msg, "warning")
        return redirect(url_for("backoffice_v3_web.get_generated_user"), code=303)

    try:
        user_data = users_generator.GenerateUserData(
            age=form.age.data, is_email_validated=form.is_email_validated.data, is_beneficiary=form.is_beneficiary.data
        )
        user = users_generator.generate_user(user_data=user_data)
    except users_exceptions.UserGenerationForbiddenException:
        raise NotFound()

    return redirect(url_for("backoffice_v3_web.get_generated_user", userId=user.id), code=303)


def _get_user_if_exists(user_id: str | None) -> users_models.User | None:
    if user_id is None:
        return None

    return users_models.User.query.get(int(user_id))
