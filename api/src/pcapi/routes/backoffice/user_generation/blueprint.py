from urllib.parse import urlencode

from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from werkzeug.exceptions import NotFound

from pcapi import settings
from pcapi.core import token as token_utils
from pcapi.core.users import constants as users_constants
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import generator as users_generator
from pcapi.core.users import models as users_models
from pcapi.routes.backoffice import blueprint
from pcapi.routes.backoffice import utils

from . import forms


@blueprint.backoffice_web.route("/admin/user-generator", methods=["GET"])
@utils.custom_login_required(redirect_to=".home")
def get_generated_user() -> utils.BackofficeResponse:
    form = forms.UserGeneratorForm()
    user = _get_user_if_exists(utils.get_query_params().get("userId"))
    token = utils.get_query_params().get("accessToken")
    link_to_app = None
    link_to_ubble_mock = None
    if token:
        path = "signup-confirmation"
        universal_link_url = f"{settings.WEBAPP_V2_URL}/{path}"
        params = {"token": token}
        link_to_app = universal_link_url + f"?{urlencode(params)}"

    if user and settings.UBBLE_MOCK_CONFIG_URL:
        link_to_ubble_mock = settings.UBBLE_MOCK_CONFIG_URL + f"?{urlencode({'userId': user.id})}"

    return render_template(
        "admin/users_generator.html",
        link_to_app=link_to_app,
        link_to_ubble_mock=link_to_ubble_mock,
        user=user,
        form=form,
        dst=url_for("backoffice_web.generate_user"),
    )


@blueprint.backoffice_web.route("/admin/user-generator", methods=["POST"])
@utils.custom_login_required(redirect_to=".home")
def generate_user() -> utils.BackofficeResponse:
    form = forms.UserGeneratorForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.get_generated_user"), code=303)

    # >18yo user cannot be identified with Educonnect
    age = form.age.data
    id_provider = form.id_provider.data
    transition_17_18 = form.transition_17_18.data
    if (
        not transition_17_18
        and age >= users_constants.ELIGIBILITY_AGE_18
        and id_provider == users_generator.GeneratedIdProvider.EDUCONNECT.name
    ):
        flash("Un utilisateur de plus de 18 ans ne peut pas être identifié via Educonnect", "warning")
        return redirect(url_for("backoffice_web.get_generated_user"), code=303)

    # <18yo user cannot validate phone number
    step = form.step.data
    if (
        age < users_constants.ELIGIBILITY_AGE_18
        and step == users_generator.GeneratedSubscriptionStep.PHONE_VALIDATION.name
    ):
        flash("Un utilisateur de moins de 18 ans ne peut pas valider son numéro de téléphone", "warning")
        return redirect(url_for("backoffice_web.get_generated_user"), code=303)

    try:
        user_data = users_generator.GenerateUserData(
            age=form.age.data,
            id_provider=users_generator.GeneratedIdProvider[form.id_provider.data],
            step=users_generator.GeneratedSubscriptionStep[form.step.data],
            transition_17_18=form.transition_17_18.data,
        )
        user = users_generator.generate_user(user_data=user_data)
    except users_exceptions.UserGenerationForbiddenException:
        raise NotFound()

    token = token_utils.Token.create(
        token_utils.TokenType.EMAIL_VALIDATION, users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME, user.id
    )
    return redirect(
        url_for("backoffice_web.get_generated_user", userId=user.id, accessToken=token.encoded_token), code=303
    )


def _get_user_if_exists(user_id: str | None) -> users_models.User | None:
    if user_id is None:
        return None

    return users_models.User.query.get(int(user_id))
