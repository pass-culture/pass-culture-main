import logging

from flask import abort
from flask import jsonify
from flask import request
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from jwt import InvalidTokenError
import pydantic

from pcapi.core.users import api as users_api
from pcapi.core.users import email as email_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as user_models
from pcapi.core.users import repository as users_repo
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import transaction
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import beneficiaries as serialization_beneficiaries
from pcapi.routes.serialization.beneficiaries import BeneficiaryAccountResponse
from pcapi.routes.serialization.beneficiaries import ChangeBeneficiaryEmailBody
from pcapi.routes.serialization.beneficiaries import ChangeBeneficiaryEmailRequestBody
from pcapi.routes.serialization.beneficiaries import ChangeEmailTokenContent
from pcapi.routes.serialization.beneficiaries import PatchBeneficiaryBodyModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.login_manager import stamp_session
from pcapi.utils.rate_limiting import email_rate_limiter
from pcapi.utils.rate_limiting import ip_rate_limiter
from pcapi.validation.routes.users import check_valid_signin


logger = logging.getLogger(__name__)


@private_api.route("/beneficiaries/current", methods=["GET"])
@login_required
@spectree_serialize(response_model=BeneficiaryAccountResponse)
def get_beneficiary_profile() -> BeneficiaryAccountResponse:
    user = current_user._get_current_object()
    response = BeneficiaryAccountResponse.from_orm(user)

    return response


@private_api.route("/beneficiaries/current", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=BeneficiaryAccountResponse)
def patch_beneficiary(body: PatchBeneficiaryBodyModel) -> BeneficiaryAccountResponse:
    user: user_models.User = current_user._get_current_object()
    # This route should ony be used by "beneficiary" users because it
    # allows to update different infos from `/users/current`.
    if not user.has_beneficiary_role and not user.isAdmin:
        abort(403)
    users_api.update_user_info(user, **body.dict(exclude_unset=True))
    return BeneficiaryAccountResponse.from_orm(user)


@private_api.route("/beneficiaries/change_email_request", methods=["PUT"])
@login_required
@spectree_serialize(on_success_status=204, on_error_statuses=[401, 503])
def change_beneficiary_email_request(body: ChangeBeneficiaryEmailRequestBody) -> None:
    errors = ApiErrors()
    errors.status_code = 401

    try:
        user = users_repo.get_user_with_credentials(current_user.email, body.password)
    except users_exceptions.InvalidIdentifier as exc:
        errors.add_error("password", "Mot de passe incorrect")
        raise errors from exc
    except users_exceptions.UnvalidatedAccount as exc:
        errors.add_error("identifier", "Ce compte n'est pas validé.")
        raise errors from exc

    expiration_date = email_api.generate_token_expiration_date()
    if not email_api.send_user_emails_for_email_change(user, body.new_email, expiration_date):
        errors.status_code = 503
        errors.add_error("email", "L'envoi d'email a échoué")
        raise errors


@private_api.route("/beneficiaries/change_email", methods=["PUT"])
@spectree_serialize(on_success_status=204, on_error_statuses=[400])
def change_beneficiary_email(body: ChangeBeneficiaryEmailBody) -> None:
    try:
        payload = ChangeEmailTokenContent.from_token(body.token)
        users_api.change_user_email(
            current_email=payload.current_email,
            new_email=payload.new_email,
        )
    except pydantic.ValidationError:
        # Do nothing to avoid a breaking change
        pass
    except InvalidTokenError as error:
        errors = ApiErrors()
        errors.status_code = 400
        raise errors from error
    except (users_exceptions.EmailExistsError, users_exceptions.UserDoesNotExist):
        # Do nothing to avoid a breaking change
        pass


# @debt api-migration
@private_api.route("/beneficiaries/signin", methods=["POST"])
@email_rate_limiter()
@ip_rate_limiter()
def signin_beneficiary() -> tuple[str, int]:
    json = request.get_json()
    identifier = json.get("identifier")
    password = json.get("password")
    check_valid_signin(identifier, password)
    errors = ApiErrors()
    errors.status_code = 401
    try:
        user = users_repo.get_user_with_credentials(identifier, password)
    except users_exceptions.InvalidIdentifier as exc:
        errors.add_error("signin", "Identifiant ou mot de passe incorrect")
        raise errors from exc
    except users_exceptions.UnvalidatedAccount as exc:
        errors.add_error("identifier", "Ce compte n'est pas validé.")
        raise errors from exc
    login_user(user)
    stamp_session(user)
    return jsonify(), 200


@private_api.route("/send_phone_validation_code", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=204)
def send_phone_validation_code(body: serialization_beneficiaries.SendPhoneValidationRequest) -> None:
    user = current_user._get_current_object()
    try:
        if body.phone_number:
            users_api.change_user_phone_number(user, body.phone_number)
        users_api.send_phone_validation_code(user)
    except users_exceptions.UserPhoneNumberAlreadyValidated:
        raise ApiErrors({"message": "Le numéro de téléphone est déjà validé"}, status_code=400)
    except users_exceptions.UserWithoutPhoneNumberException:
        raise ApiErrors({"message": "Le numéro de téléphone est invalide"}, status_code=400)
    except users_exceptions.InvalidPhoneNumber:
        raise ApiErrors(
            {"message": "Le numéro de téléphone est invalide", "code": "INVALID_PHONE_NUMBER"}, status_code=400
        )
    except users_exceptions.PhoneVerificationException:
        raise ApiErrors({"message": "L'envoi du code a échoué", "code": "CODE_SENDING_FAILURE"}, status_code=400)


@private_api.route("/validate_phone_number", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=204)
def validate_phone_number(body: serialization_beneficiaries.ValidatePhoneNumberRequest) -> None:
    user = current_user._get_current_object()

    with transaction():
        try:
            users_api.validate_phone_number_and_activate_user(user, body.code)
        except users_exceptions.ExpiredCode:
            raise ApiErrors({"message": "Le code saisi a expiré", "code": "EXPIRED_VALIDATION_CODE"}, status_code=400)
        except users_exceptions.NotValidCode:
            raise ApiErrors({"message": "Le code est invalide", "code": "INVALID_VALIDATION_CODE"}, status_code=400)
        except users_exceptions.InvalidPhoneNumber:
            raise ApiErrors(
                {"message": "Le numéro de téléphone est invalide", "code": "INVALID_PHONE_NUMBER"}, status_code=400
            )
        except users_exceptions.PhoneVerificationException:
            raise ApiErrors({"message": "L'envoi du code a échoué", "code": "CODE_SENDING_FAILURE"}, status_code=400)
