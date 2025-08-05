import datetime
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
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.pro.utils import get_connect_as
from pcapi.utils.transaction_manager import mark_transaction_as_invalid

from . import forms


logger = logging.getLogger(__name__)

dev_blueprint = utils.child_backoffice_blueprint(
    "dev",
    __name__,
    url_prefix="/dev",
)


@dev_blueprint.route("/components", methods=["GET"])
@utils.custom_login_required(redirect_to="backoffice_web.home")
def components() -> utils.BackofficeResponse:
    if not settings.ENABLE_BO_COMPONENT_PAGE:
        raise NotFound()

    connect_as = get_connect_as(
        object_type="user",
        object_id=12,
        pc_pro_path="/home",
    )

    return render_template(
        "dev/components.html",
        simple_form=forms.SimpleComponentsForm(),
        rows={"pages": 5},
        next_pages_urls=[(i, str(i)) for i in range(6)],
        connect_as=connect_as,
    )


@dev_blueprint.route("/user-generator", methods=["GET"])
@utils.custom_login_required(redirect_to="backoffice_web.home")
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
        if expiration_timestamp := utils.get_query_params().get("expirationTimestamp"):
            params["expiration_timestamp"] = expiration_timestamp
        if user:
            params["email"] = user.email
        if set(params) == {"email", "expiration_timestamp", "token"}:
            link_to_app = f"{universal_link_url}?{urlencode(params)}"

    if user and settings.UBBLE_MOCK_CONFIG_URL:
        link_to_ubble_mock = f"{settings.UBBLE_MOCK_CONFIG_URL}?{urlencode({'userId': user.id})}"

    if user:
        birth_date = user.dateOfBirth.date() if user.dateOfBirth else None
        id_document_number = f"{user.id:012}"
        ubble_form = forms.UbbleConfigurationForm(birth_date=birth_date, id_document_number=id_document_number)
    else:
        ubble_form = forms.UbbleConfigurationForm()

    return render_template(
        "dev/users_generator.html",
        link_to_app=link_to_app,
        link_to_ubble_mock=link_to_ubble_mock,
        user=user,
        form=form,
        dst=url_for("backoffice_web.dev.generate_user"),
        ubble_configuration_form=ubble_form,
    )


@dev_blueprint.route("/user-generator", methods=["POST"])
@utils.custom_login_required(redirect_to="backoffice_web.home")
def generate_user() -> utils.BackofficeResponse:
    form = forms.UserGeneratorForm()

    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.dev.get_generated_user"), code=303)

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
        return redirect(url_for("backoffice_web.dev.get_generated_user"), code=303)

    # <18yo user cannot validate phone number
    step = form.step.data
    if (
        age < users_constants.ELIGIBILITY_AGE_18
        and step == users_generator.GeneratedSubscriptionStep.PHONE_VALIDATION.name
    ):
        mark_transaction_as_invalid()
        flash("Un utilisateur de moins de 18 ans ne peut pas valider son numéro de téléphone", "warning")
        return redirect(url_for("backoffice_web.dev.get_generated_user"), code=303)

    # 15 to 16 years old only validate their email and complete their profile
    if age in users_constants.ELIGIBILITY_FREE_RANGE and step not in [
        users_generator.GeneratedSubscriptionStep.EMAIL_VALIDATION.name,
        users_generator.GeneratedSubscriptionStep.PROFILE_COMPLETION.name,
        users_generator.GeneratedSubscriptionStep.BENEFICIARY.name,
    ]:
        mark_transaction_as_invalid()
        flash(
            "Un utilisateur de 15 à 16 ans ne peut que valider son email, compléter son profil ou être bénéficiaire",
            "warning",
        )
        return redirect(url_for("backoffice_web.dev.get_generated_user"), code=303)

    try:
        raw_date_created = form.date_created.data
        user_data = users_generator.GenerateUserData(
            age=form.age.data,
            id_provider=users_generator.GeneratedIdProvider[form.id_provider.data],
            step=users_generator.GeneratedSubscriptionStep[form.step.data],
            transition_17_18=form.transition_17_18.data,
            date_created=datetime.datetime(raw_date_created.year, raw_date_created.month, raw_date_created.day),
        )
        user = users_generator.generate_user(user_data=user_data)
    except users_exceptions.UserGenerationForbiddenException:
        raise NotFound()

    token = token_utils.Token.create(
        token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION, users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME, user.id
    )
    expiration_date = (
        token.get_expiration_date_from_token()
        or datetime.datetime.utcnow() + users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME
    )
    expiration_timestamp = int(expiration_date.timestamp())
    return redirect(
        url_for(
            "backoffice_web.dev.get_generated_user",
            userId=user.id,
            accessToken=token.encoded_token,
            expirationTimestamp=expiration_timestamp,
        ),
        code=303,
    )


def _get_user_if_exists(user_id: str | None) -> users_models.User | None:
    if user_id is None:
        return None

    return db.session.query(users_models.User).filter_by(id=int(user_id)).one_or_none()


@dev_blueprint.route("/delete", methods=["GET"])
@utils.custom_login_required(redirect_to="backoffice_web.home")
def get_user_deletion_form() -> str:
    form = forms.UserDeletionForm()
    return render_template("dev/users_deletion.html", form=form)


@dev_blueprint.route("/delete", methods=["POST"])
@utils.custom_login_required(redirect_to="backoffice_web.home")
def delete_user() -> utils.BackofficeResponse:
    if not settings.ENABLE_TEST_USER_GENERATION:
        raise NotFound()

    form = forms.UserDeletionForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return render_template("dev/users_deletion.html", form=form), 400

    email = form.email.data
    user = db.session.query(users_models.User).filter_by(email=email).one_or_none()
    if not user:
        mark_transaction_as_invalid()
        flash(
            Markup("L'adresse email <b>{email}</b> n'a pas été trouvée.").format(email=email),
            "warning",
        )
        return render_template("dev/users_deletion.html", form=form), 400

    try:
        db.session.query(users_models.User).filter_by(id=user.id).delete()
        db.session.flush()
    except IntegrityError as e:
        logger.info(e)
        mark_transaction_as_invalid()
        flash(
            Markup("Le compte de l'utilisateur <b>{email}</b> n'a pas pu être supprimé.").format(email=email),
            "warning",
        )
        return redirect(url_for("backoffice_web.dev.delete_user"), code=303)

    flash(
        Markup("Le compte de l'utilisateur <b>{email}</b> a été supprimé").format(email=email),
        "success",
    )
    return redirect(url_for("backoffice_web.dev.delete_user"), code=303)


@dev_blueprint.route("/<int:user_id>/ubble/configuration", methods=["POST"])
@utils.custom_login_required(redirect_to=".home")
def configure_ubble_v2_response(user_id: int) -> utils.BackofficeResponse:
    user = _get_user_if_exists(str(user_id))
    if user is None:
        mark_transaction_as_invalid()
        flash(f"L'utilisateur {user_id} n'a pas été trouvé", "warning")
        return redirect(url_for("backoffice_web.dev.get_generated_user"), code=404)

    form = forms.UbbleConfigurationForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.dev.get_generated_user"), code=303)

    # Ubble response codes can be tested by inserting the ones we want in the external applicant id of the Ubble
    # applicant. See https://docs.ubble.ai/#section/Testing/Declined-verification-on-retry-after-checks-inconclusive
    final_response_code = form.final_response_code.data
    intermediate_response_code = form.intermediate_response_code.data
    if intermediate_response_code:
        external_applicant_id = f"eaplt_{intermediate_response_code}A{final_response_code}".ljust(32, "0")
    else:
        external_applicant_id = f"eaplt_{final_response_code}".ljust(32, "0")

    ubble_fraud_check = fraud_models.BeneficiaryFraudCheck(
        user=user,
        eligibilityType=user.eligibility,
        type=fraud_models.FraudCheckType.UBBLE,
        thirdPartyId="",
        status=fraud_models.FraudCheckStatus.STARTED,
        resultContent=fraud_models.UbbleContent(
            birth_date=form.birth_date.data,
            external_applicant_id=external_applicant_id,
            id_document_number=form.id_document_number.data,
        ).dict(exclude_none=True),
    )
    db.session.add(ubble_fraud_check)
    db.session.flush()

    flash("La réponse d'Ubble v2 a été configurée pour cet utilisateur", "success")

    token = token_utils.Token.get_token(token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION, user.id)
    params = {}
    if token:
        params["accessToken"] = token.encoded_token
        expiration_date = (
            token.get_expiration_date_from_token()
            or datetime.datetime.utcnow() + users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME
        )
        params["expirationTimestamp"] = str(int(expiration_date.timestamp()))
        params["email"] = user.email
    return redirect(url_for("backoffice_web.dev.get_generated_user", userId=user.id, **params), code=303)
