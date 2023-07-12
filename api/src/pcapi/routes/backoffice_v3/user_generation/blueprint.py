import datetime
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from werkzeug.exceptions import NotFound
from pcapi import settings

from pcapi.core.users import constants as users_constants
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users.api import generate_and_save_token
import pcapi.core.users.generator as users_generator
from pcapi.routes.backoffice_v3 import blueprint
from pcapi.routes.backoffice_v3 import utils
from pcapi.utils.urls import generate_firebase_dynamic_link

from . import forms


@blueprint.backoffice_v3_web.route("/admin/user-generator", methods=["GET"])
@utils.custom_login_required(redirect_to=".home")
def get_generated_user() -> utils.BackofficeResponse:
    form = forms.UserGeneratorForm()
    user = _get_user_if_exists(utils.get_query_params().get("userId"))
    token = utils.get_query_params().get("accessToken")
    link_to_app = None
    if token:
        link_to_app = generate_firebase_dynamic_link(
            path="",
            params={"token": token, "email": user.email},
        )

    return render_template(
        "admin/users_generator.html",
        link_to_app=link_to_app,
        user=user,
        form=form,
        dst=url_for("backoffice_v3_web.generate_user"),
    )


@blueprint.backoffice_v3_web.route("/admin/user-generator", methods=["POST"])
@utils.custom_login_required(redirect_to=".home")
def generate_user() -> utils.BackofficeResponse:
    form = forms.UserGeneratorForm()

    if not form.validate():
        error_msg = utils.build_form_error_msg(form)
        flash(error_msg, "warning")
        return redirect(url_for("backoffice_v3_web.get_generated_user"), code=303)

    # >18yo user cannot be identified with Educonnect
    age = form.age.data
    id_provider = form.id_provider.data
    if age >= users_constants.ELIGIBILITY_AGE_18 and id_provider == users_generator.GeneratedIdProvider.EDUCONNECT.name:
        flash("Un utilisateur de plus de 18 ans ne peut pas être identifié via Educonnect", "warning")
        return redirect(url_for("backoffice_v3_web.get_generated_user"), code=303)

    # <18yo user cannot validate phone number
    step = form.step.data
    if (
        age < users_constants.ELIGIBILITY_AGE_18
        and step == users_generator.GeneratedSubscriptionStep.PHONE_VALIDATION.name
    ):
        flash("Un utilisateur de moins de 18 ans ne peut pas valider son numéro de téléphone", "warning")
        return redirect(url_for("backoffice_v3_web.get_generated_user"), code=303)

    try:
        user_data = users_generator.GenerateUserData(
            age=form.age.data,
            id_provider=users_generator.GeneratedIdProvider[form.id_provider.data],
            step=users_generator.GeneratedSubscriptionStep[form.step.data],
        )
        user = users_generator.generate_user(user_data=user_data)
    except users_exceptions.UserGenerationForbiddenException:
        raise NotFound()

    token = generate_and_save_token(
        user,
        users_models.TokenType.USER_GENERATOR,
        datetime.datetime.utcnow() + users_constants.USER_GENERATOR_TOKEN_LIFE_TIME,
    )
    return redirect(url_for("backoffice_v3_web.get_generated_user", userId=user.id, accessToken=token.id), code=303)


def _get_user_if_exists(user_id: str | None) -> users_models.User | None:
    if user_id is None:
        return None

    return users_models.User.query.get(int(user_id))
