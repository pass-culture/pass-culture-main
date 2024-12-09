import logging
from urllib.parse import urlencode

from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from markupsafe import Markup
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound

from pcapi import settings
from pcapi.core import token as token_utils
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import constants as users_constants
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import generator as users_generator
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid
from pcapi.routes.backoffice import blueprint
from pcapi.routes.backoffice import utils

from . import forms


logger = logging.getLogger(__name__)


@blueprint.backoffice_web.route("/admin/user-generator", methods=["GET"])
@atomic()
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
        ubble_configuration_form=forms.UbbleConfigurationForm(),
    )


@blueprint.backoffice_web.route("/admin/user-generator", methods=["POST"])
@atomic()
@utils.custom_login_required(redirect_to=".home")
def generate_user() -> utils.BackofficeResponse:
    form = forms.UserGeneratorForm()

    if not form.validate():
        mark_transaction_as_invalid()
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
        mark_transaction_as_invalid()
        flash("Un utilisateur de plus de 18 ans ne peut pas être identifié via Educonnect", "warning")
        return redirect(url_for("backoffice_web.get_generated_user"), code=303)

    # <18yo user cannot validate phone number
    step = form.step.data
    if (
        age < users_constants.ELIGIBILITY_AGE_18
        and step == users_generator.GeneratedSubscriptionStep.PHONE_VALIDATION.name
    ):
        mark_transaction_as_invalid()
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

    return users_models.User.query.filter_by(id=int(user_id)).one_or_none()


@blueprint.backoffice_web.route("/admin/delete", methods=["GET"])
@atomic()
@utils.custom_login_required(redirect_to=".home")
def get_user_deletion_form() -> str:
    form = forms.UserDeletionForm()
    return render_template("admin/users_deletion.html", form=form)


@blueprint.backoffice_web.route("/admin/delete", methods=["POST"])
@atomic()
@utils.custom_login_required(redirect_to=".home")
def delete_user() -> utils.BackofficeResponse:
    if not settings.ENABLE_TEST_USER_GENERATION:
        raise NotFound()

    form = forms.UserDeletionForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return render_template("admin/users_deletion.html", form=form), 400

    email = form.email.data
    user = users_models.User.query.filter_by(email=email).one_or_none()
    if not user:
        mark_transaction_as_invalid()
        flash(
            Markup("L'adresse email <b>{email}</b> n'a pas été trouvée.").format(email=email),
            "warning",
        )
        return render_template("admin/users_deletion.html", form=form), 400

    try:
        users_models.User.query.filter_by(id=user.id).delete()
        db.session.flush()
    except IntegrityError as e:
        logger.info(e)
        mark_transaction_as_invalid()
        flash(
            Markup("Le compte de l'utilisateur <b>{email}</b> n'a pas pu être supprimé.").format(email=email),
            "warning",
        )
        return redirect(url_for("backoffice_web.delete_user"), code=303)

    flash(
        Markup("Le compte de l'utilisateur <b>{email}</b> a été supprimé").format(email=email),
        "success",
    )
    return redirect(url_for("backoffice_web.delete_user"), code=303)


@blueprint.backoffice_web.route("/<int:user_id>/ubble/configuration", methods=["POST"])
@atomic()
@utils.custom_login_required(redirect_to=".home")
def configure_ubble_v2_response(user_id: int) -> utils.BackofficeResponse:
    user = _get_user_if_exists(str(user_id))
    if user is None:
        mark_transaction_as_invalid()
        flash(f"L'utilisateur {user_id} n'a pas été trouvé", "warning")
        return redirect(url_for("backoffice_web.get_generated_user"), code=404)

    form = forms.UbbleConfigurationForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return render_template("backoffice_web.get_generated_user", form=form), 400

    # Ubble response codes can be tested by inserting the ones we want in the external applicant id of the Ubble
    # applicant. See https://docs.ubble.ai/#section/Testing/Declined-verification-on-retry-after-checks-inconclusive
    second_response_code = form.second_response_code.data
    if second_response_code:
        applicant_id_suffix = "A" + second_response_code.ljust(20, "0")
    else:
        applicant_id_suffix = "".ljust(21, "0")

    first_response_code = form.first_response_code.data
    external_applicant_id = f"eaplt_{first_response_code}{applicant_id_suffix}"
    ubble_fraud_check = fraud_models.BeneficiaryFraudCheck(
        user=user,
        eligibilityType=user.eligibility,
        type=fraud_models.FraudCheckType.UBBLE,
        thirdPartyId="",
        status=fraud_models.FraudCheckStatus.STARTED,
        resultContent=fraud_models.UbbleContent(
            birth_date=form.birth_date.data, external_applicant_id=external_applicant_id
        ).dict(exclude_none=True),
    )
    db.session.add(ubble_fraud_check)
    db.session.flush()

    flash("La réponse d'Ubble v2 a été configurée pour cet utilisateur", "success")

    token = token_utils.Token.get_token(token_utils.TokenType.EMAIL_VALIDATION, user.id)
    access_token = token.encoded_token if token else None
    return redirect(url_for("backoffice_web.get_generated_user", userId=user.id, accessToken=access_token), code=303)
