from datetime import datetime
import logging

from flask import current_app as app
import pydantic.v1 as pydantic_v1
import sqlalchemy as sa

from pcapi.connectors import api_recaptcha
from pcapi.connectors import google_oauth
from pcapi.core import token as token_utils
import pcapi.core.bookings.exceptions as bookings_exceptions
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.fraud.phone_validation import sending_limit
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.subscription.phone_validation import api as phone_validation_api
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.users import api
from pcapi.core.users import constants
from pcapi.core.users import email as email_api
from pcapi.core.users import exceptions
from pcapi.core.users.email import repository as email_repository
import pcapi.core.users.models as users_models
from pcapi.core.users.repository import find_user_by_email
from pcapi.domain import password
from pcapi.models import api_errors
from pcapi.models.feature import FeatureToggle
from pcapi.repository import transaction
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.security import authenticated_maybe_inactive_user_required
from pcapi.routes.native.v1.api_errors import account as account_errors
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint
from .serialization import account as serializers
from .serialization import authentication as auth_serializers


logger = logging.getLogger(__name__)


@blueprint.native_route("/me", methods=["GET"])
@spectree_serialize(
    response_model=serializers.UserProfileResponse,
    on_success_status=200,
    api=blueprint.api,
)
@authenticated_and_active_user_required
def get_user_profile(user: users_models.User) -> serializers.UserProfileResponse:
    return serializers.UserProfileResponse.from_orm(user)


@blueprint.native_route("/profile", methods=["POST"])
@spectree_serialize(
    response_model=serializers.UserProfileResponse,
    on_success_status=200,
    api=blueprint.api,
)
@authenticated_and_active_user_required
def update_user_profile(
    user: users_models.User, body: serializers.UserProfileUpdateRequest
) -> serializers.UserProfileResponse:
    api.update_notification_subscription(user, body.subscriptions, body.origin)
    external_attributes_api.update_external_user(user)
    return serializers.UserProfileResponse.from_orm(user)


@blueprint.native_route("/reset_recredit_amount_to_show", methods=["POST"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=serializers.UserProfileResponse)
@authenticated_and_active_user_required
def reset_recredit_amount_to_show(user: users_models.User) -> serializers.UserProfileResponse:
    api.reset_recredit_amount_to_show(user)

    return serializers.UserProfileResponse.from_orm(user)


@blueprint.native_route("/profile/update_email", methods=["POST"])
@blueprint.api.validate(deprecated=True)
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
def update_user_email(user: users_models.User, body: serializers.UserProfileEmailUpdate) -> None:
    try:
        email_api.request_email_update_with_credentials(user, body.email, body.password)
    except exceptions.EmailUpdateTokenExists:
        raise account_errors.EmailUpdatePendingError()
    except exceptions.EmailUpdateLimitReached:
        raise account_errors.EmailUpdateLimitError()
    except exceptions.EmailExistsError:
        # Returning an error message might help the end client find
        # existing email addresses.
        return
    except exceptions.EmailUpdateInvalidPassword:
        raise account_errors.WrongPasswordError()


@blueprint.native_route("/profile/email_update/status", methods=["GET"])
@blueprint.api.validate(deprecated=True)
@spectree_serialize(
    on_success_status=200,
    api=blueprint.api,
    response_model=serializers.EmailUpdateStatus,
)
@authenticated_and_active_user_required
def get_email_update_status(user: users_models.User) -> serializers.EmailUpdateStatus:
    latest_email_update_event = email_repository.get_email_update_latest_event(user)
    if not latest_email_update_event:
        raise api_errors.ResourceNotFoundError
    return serializers.EmailUpdateStatus(
        newEmail=latest_email_update_event.newEmail or "",
        expired=(email_api.get_active_token_expiration(user) or datetime.min) < datetime.utcnow(),
        status=latest_email_update_event.eventType,
    )


@blueprint.native_route("/profile/email_update/confirm", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
def confirm_email_update(body: serializers.ChangeBeneficiaryEmailBody) -> None:
    try:
        email_api.update.confirm_email_update_request_and_send_mail(body.token)
    except pydantic_v1.ValidationError:
        raise api_errors.ApiErrors(
            {"code": "INVALID_EMAIL", "message": "Adresse email invalide"},
            status_code=400,
        )
    except (exceptions.InvalidToken, exceptions.EmailExistsError):
        raise api_errors.ApiErrors(
            {"code": "INVALID_TOKEN", "message": "aucune demande de changement d'email en cours"},
            status_code=401,
        )


@blueprint.native_route("/profile/email_update/cancel", methods=["POST"])
@spectree_serialize(
    on_success_status=204,
    api=blueprint.api,
)
def cancel_email_update(body: serializers.ChangeBeneficiaryEmailBody) -> None:
    try:
        email_api.update.cancel_email_update_request(body.token)
    except exceptions.InvalidToken:
        raise api_errors.ApiErrors(
            {"code": "INVALID_TOKEN", "message": "aucune demande de changement d'email en cours"},
            status_code=401,
        )


@blueprint.native_route("/profile/email_update/validate", methods=["PUT"])
@spectree_serialize(response_model=serializers.ChangeBeneficiaryEmailResponse, on_success_status=200, api=blueprint.api)
def validate_user_email(body: serializers.ChangeBeneficiaryEmailBody) -> serializers.ChangeBeneficiaryEmailResponse:
    try:
        user = email_api.update.validate_email_update_request(body.token)
    except pydantic_v1.ValidationError:
        raise api_errors.ApiErrors(
            {"code": "INVALID_EMAIL", "message": "Adresse email invalide"},
            status_code=400,
        )
    except exceptions.InvalidToken:
        raise api_errors.ApiErrors(
            {"code": "INVALID_TOKEN", "message": "Token invalide"},
            status_code=400,
        )
    except exceptions.EmailExistsError:
        # Returning an error message might help the end client find
        # existing email addresses through user enumeration attacks.
        token = token_utils.Token.load_without_checking(body.token)
        user = users_models.User.query.get(token.user_id)

    if user.is_eligible and not user.is_beneficiary:
        try:
            dms_subscription_api.try_dms_orphan_adoption(user)
        except Exception:  # pylint: disable=broad-except
            logger.exception(
                "An unexpected error occurred while trying to link dms orphan to user", extra={"user_id": user.id}
            )

    return serializers.ChangeBeneficiaryEmailResponse(
        access_token=api.create_user_access_token(user),
        refresh_token=api.create_user_refresh_token(user, body.device_info),
    )


@blueprint.native_route("/profile/token_expiration", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=serializers.UpdateEmailTokenExpiration)
@authenticated_and_active_user_required
def get_email_update_token_expiration_date(user: users_models.User) -> serializers.UpdateEmailTokenExpiration:
    return serializers.UpdateEmailTokenExpiration(expiration=email_api.get_active_token_expiration(user))


@blueprint.native_route("/account", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api, on_error_statuses=[400])
def create_account(body: serializers.AccountRequest) -> None:
    if FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active():
        try:
            api_recaptcha.check_native_app_recaptcha_token(body.token)
        except api_recaptcha.ReCaptchaException:
            raise api_errors.ApiErrors({"token": "The given token is not valid"})

    password.check_password_strength("password", body.password)

    try:
        created_user = api.create_account(
            email=body.email,
            password=body.password,
            birthdate=body.birthdate,
            marketing_email_subscription=bool(body.marketing_email_subscription),
            is_email_validated=False,
            apps_flyer_user_id=body.apps_flyer_user_id,
            apps_flyer_platform=body.apps_flyer_platform,
            firebase_pseudo_id=body.firebase_pseudo_id,
        )

        if FeatureToggle.WIP_ENABLE_TRUSTED_DEVICE.is_active() and body.trusted_device is not None:
            api.save_trusted_device(device_info=body.trusted_device, user=created_user)

    except exceptions.UserAlreadyExistsException:
        user = find_user_by_email(body.email)
        assert user is not None
        api.handle_create_account_with_existing_email(user)

    except exceptions.UnderAgeUserException:
        raise api_errors.ApiErrors({"dateOfBirth": "The birthdate is invalid"})


@blueprint.native_route("/oauth/google/account", methods=["POST"])
@spectree_serialize(response_model=auth_serializers.SigninResponse, api=blueprint.api, on_error_statuses=[400])
def create_account_with_google_sso(body: serializers.GoogleAccountRequest) -> auth_serializers.SigninResponse:
    if FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active():
        try:
            api_recaptcha.check_native_app_recaptcha_token(body.token)
        except api_recaptcha.ReCaptchaException as e:
            raise api_errors.ApiErrors({"token": "The given token is not valid"}) from e

    try:
        account_creation_token = token_utils.UUIDToken.load_and_check(
            body.account_creation_token, token_utils.TokenType.ACCOUNT_CREATION
        )
        google_user = google_oauth.GoogleUser.model_validate(account_creation_token.data)
        account_creation_token.expire()
    except exceptions.ExpiredToken as e:
        raise api_errors.ApiErrors(
            {
                "code": "SSO_ACCOUNT_CREATION_TIMEOUT",
                "general": ["La demande de création de compte a mis trop de temps."],
            }
        ) from e
    except exceptions.InvalidToken as e:
        raise api_errors.ApiErrors(
            {
                "code": "SSO_INVALID_ACCOUNT_CREATION",
                "general": ["La demande de création de compte est invalide."],
            }
        ) from e

    if not google_user.email_verified:
        raise api_errors.ApiErrors({"code": "EMAIL_NOT_VALIDATED", "general": ["L'email n'a pas été validé."]})

    try:
        created_user = api.create_account(
            email=google_user.email,
            password=None,
            sso_provider="google",
            sso_user_id=google_user.sub,
            birthdate=body.birthdate,
            marketing_email_subscription=bool(body.marketing_email_subscription),
            is_email_validated=True,
            apps_flyer_user_id=body.apps_flyer_user_id,
            apps_flyer_platform=body.apps_flyer_platform,
            firebase_pseudo_id=body.firebase_pseudo_id,
        )

        if FeatureToggle.WIP_ENABLE_TRUSTED_DEVICE.is_active() and body.trusted_device is not None:
            api.save_trusted_device(device_info=body.trusted_device, user=created_user)

    except exceptions.UserAlreadyExistsException:
        raise api_errors.ApiErrors({"email": [f"Un compte existe déjà pour l'adresse mail Google {google_user.email}"]})

    except exceptions.UnderAgeUserException:
        raise api_errors.ApiErrors({"dateOfBirth": "The birthdate is invalid"})

    try:
        dms_subscription_api.try_dms_orphan_adoption(created_user)
    except Exception:  # pylint: disable=broad-except
        logger.exception(
            "An unexpected error occurred while trying to link dms orphan to user", extra={"user_id": created_user.id}
        )

    return auth_serializers.SigninResponse(
        access_token=api.create_user_access_token(created_user),
        refresh_token=api.create_user_refresh_token(created_user, body.trusted_device),
        account_state=created_user.account_state,
    )


@blueprint.native_route("/resend_email_validation", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api, on_error_statuses=[400, 429])
def resend_email_validation(body: serializers.ResendEmailValidationRequest) -> None:
    user = find_user_by_email(body.email)
    if not user or not user.isActive:
        return
    try:
        if user.isEmailValidated:
            api.request_password_reset(user)
        else:
            api.check_email_validation_resends_count(user)
            api.increment_email_validation_resends_count(user)
            api.request_email_confirmation(user)
    except exceptions.EmailValidationLimitReached:
        raise api_errors.ApiErrors(
            {"message": "Le nombre de tentatives maximal est dépassé.", "code": "TOO_MANY_EMAIL_VALIDATION_RESENDS"},
            status_code=429,
        )


@blueprint.native_route("/email_validation_remaining_resends/<email>", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.EmailValidationRemainingResendsResponse)
def email_validation_remaining_resends(email: str) -> serializers.EmailValidationRemainingResendsResponse | None:
    user = find_user_by_email(email)
    if not user:
        return serializers.EmailValidationRemainingResendsResponse(remainingResends=0, counterResetDatetime=None)

    remaining_resends = api.get_remaining_email_validation_resends(user)
    expiration_time = api.get_email_validation_resends_limitation_expiration_time(user)

    return serializers.EmailValidationRemainingResendsResponse(
        remainingResends=remaining_resends, counterResetDatetime=expiration_time
    )


def _log_failure_code(phone_number: str, code: str) -> None:
    logger.warning("Failed to send phone validation code", extra={"number": phone_number, "code": code})


@blueprint.native_route("/send_phone_validation_code", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_and_active_user_required
def send_phone_validation_code(user: users_models.User, body: serializers.SendPhoneValidationRequest) -> None:
    try:
        phone_validation_api.send_phone_validation_code(user, body.phoneNumber)

    except phone_validation_exceptions.SMSSendingLimitReached:
        error = {"code": "TOO_MANY_SMS_SENT", "message": "Nombre de tentatives maximal dépassé"}
        _log_failure_code(body.phoneNumber, error["code"])
        raise api_errors.ApiErrors(error, status_code=400)

    except phone_validation_exceptions.UserPhoneNumberAlreadyValidated:
        error = {"code": "PHONE_NUMBER_ALREADY_VALIDATED", "message": "Le numéro de téléphone est déjà validé"}
        _log_failure_code(body.phoneNumber, error["code"])
        raise api_errors.ApiErrors(error, status_code=400)

    except phone_validation_exceptions.InvalidCountryCode:
        error = {"code": "INVALID_COUNTRY_CODE", "message": "L'indicatif téléphonique n'est pas accepté"}
        _log_failure_code(body.phoneNumber, error["code"])
        raise api_errors.ApiErrors(error, status_code=400)

    except phone_validation_exceptions.InvalidPhoneNumber:
        error = {"code": "INVALID_PHONE_NUMBER", "message": "Le numéro de téléphone est invalide"}
        _log_failure_code(body.phoneNumber, error["code"])
        raise api_errors.ApiErrors(error, status_code=400)

    except phone_validation_exceptions.PhoneAlreadyExists:
        error = {
            "code": "PHONE_ALREADY_EXISTS",
            "message": "Un compte est déjà associé à ce numéro. Renseigne un autre numéro ou connecte-toi au compte existant.",
        }
        _log_failure_code(body.phoneNumber, error["code"])
        raise api_errors.ApiErrors(error, status_code=400)

    except phone_validation_exceptions.PhoneVerificationException:
        error = {"code": "CODE_SENDING_FAILURE", "message": "L'envoi du code a échoué"}
        _log_failure_code(body.phoneNumber, error["code"])
        raise api_errors.ApiErrors(
            {"message": "L'envoi du code a échoué", "code": "CODE_SENDING_FAILURE"}, status_code=400
        )


@blueprint.native_route("/validate_phone_number", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_and_active_user_required
def validate_phone_number(user: users_models.User, body: serializers.ValidatePhoneNumberRequest) -> None:
    with transaction():
        try:
            phone_validation_api.validate_phone_number(user, body.code)
        except phone_validation_exceptions.PhoneValidationAttemptsLimitReached:
            raise api_errors.ApiErrors(
                {"message": "Le nombre de tentatives maximal est dépassé", "code": "TOO_MANY_VALIDATION_ATTEMPTS"},
                status_code=400,
            )
        except phone_validation_exceptions.NotValidCode as error:
            if error.remaining_attempts == 0:
                raise api_errors.ApiErrors(
                    {"message": "Le nombre de tentatives maximal est dépassé", "code": "TOO_MANY_VALIDATION_ATTEMPTS"},
                    status_code=400,
                )
            raise api_errors.ApiErrors(
                {
                    "message": f"Le code est invalide. Saisis le dernier code reçu par SMS. Il te reste {error.remaining_attempts} tentative{'s' if error.remaining_attempts and error.remaining_attempts > 1 else ''}.",
                    "code": "INVALID_VALIDATION_CODE",
                },
                status_code=400,
            )
        except phone_validation_exceptions.InvalidPhoneNumber:
            raise api_errors.ApiErrors(
                {"message": "Le numéro de téléphone est invalide", "code": "INVALID_PHONE_NUMBER"}, status_code=400
            )
        except phone_validation_exceptions.PhoneVerificationException:
            raise api_errors.ApiErrors(
                {"message": "L'envoi du code a échoué", "code": "CODE_SENDING_FAILURE"}, status_code=400
            )

        is_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)
        if not is_activated:
            external_attributes_api.update_external_user(user)


@blueprint.native_route("/phone_validation/remaining_attempts", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.PhoneValidationRemainingAttemptsRequest)
@authenticated_and_active_user_required
def phone_validation_remaining_attempts(user: users_models.User) -> serializers.PhoneValidationRemainingAttemptsRequest:
    remaining_attempts = sending_limit.get_remaining_sms_sending_attempts(app.redis_client, user)
    expiration_time = sending_limit.get_attempt_limitation_expiration_time(app.redis_client, user)
    return serializers.PhoneValidationRemainingAttemptsRequest(
        remainingAttempts=remaining_attempts, counterResetDatetime=expiration_time
    )


@blueprint.native_route("/account/suspend", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_and_active_user_required
def suspend_account(user: users_models.User) -> None:
    try:
        api.suspend_account(user, constants.SuspensionReason.UPON_USER_REQUEST, actor=user)
    except bookings_exceptions.BookingIsAlreadyCancelled:
        raise api_errors.ResourceGoneError()
    except bookings_exceptions.BookingIsAlreadyRefunded:
        raise api_errors.ForbiddenError()
    transactional_mails.send_user_request_to_delete_account_reception_email(user)


@blueprint.native_route("/account/suspend_for_suspicious_login", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204, on_error_statuses=[400, 401, 404])
def suspend_account_for_suspicious_login(body: serializers.SuspendAccountForSuspiciousLoginRequest) -> None:
    try:
        token = token_utils.Token.load_and_check(body.token, token_utils.TokenType.SUSPENSION_SUSPICIOUS_LOGIN)
        user = users_models.User.query.filter_by(id=token.user_id).one()
    except sa.orm.exc.NoResultFound:
        raise api_errors.ResourceNotFoundError()
    except exceptions.ExpiredToken:
        raise api_errors.ApiErrors({"reason": "Le token a expiré."}, status_code=401)
    except exceptions.InvalidToken:
        raise api_errors.ApiErrors({"reason": "Le token est invalide."})
    api.suspend_account(user, constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER, actor=user)


@blueprint.native_route("/account/suspend/token_validation/<token>", methods=["GET"])
@spectree_serialize(on_success_status=204, api=blueprint.api, on_error_statuses=[400, 401])
def account_suspension_token_validation(token: str) -> None:
    try:
        token_utils.Token.load_and_check(token, token_utils.TokenType.SUSPENSION_SUSPICIOUS_LOGIN)
    except exceptions.InvalidToken:
        raise api_errors.ApiErrors({"reason": "Le token est invalide."})


@blueprint.native_route("/account/suspension_date", methods=["GET"])
@spectree_serialize(response_model=serializers.UserSuspensionDateResponse, api=blueprint.api, on_success_status=200)
@authenticated_maybe_inactive_user_required
def get_account_suspension_date(user: users_models.User) -> serializers.UserSuspensionDateResponse:
    reason = user.suspension_reason
    if reason != constants.SuspensionReason.UPON_USER_REQUEST:
        # If the account has not been suspended upon user request, it
        # has no reason to ask for its suspension date.
        raise api_errors.ForbiddenError()

    return serializers.UserSuspensionDateResponse(date=user.suspension_date)


@blueprint.native_route("/account/suspension_status", methods=["GET"])
@spectree_serialize(response_model=serializers.UserSuspensionStatusResponse, api=blueprint.api, on_success_status=200)
@authenticated_maybe_inactive_user_required
def get_account_suspension_status(user: users_models.User) -> serializers.UserSuspensionStatusResponse:
    return serializers.UserSuspensionStatusResponse(status=user.account_state)


@blueprint.native_route("/account/unsuspend", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_maybe_inactive_user_required
def unsuspend_account(user: users_models.User) -> None:
    try:
        api.check_can_unsuspend(user)
    except exceptions.UnsuspensionNotEnabled:
        raise api_errors.ForbiddenError({"code": "ACCOUNT_UNSUSPENSION_NOT_ENABLED"})
    except exceptions.NotSuspended:
        raise api_errors.ForbiddenError({"code": "ALREADY_UNSUSPENDED"})
    except exceptions.CantAskForUnsuspension:
        raise api_errors.ForbiddenError({"code": "UNSUSPENSION_NOT_ALLOWED"})
    except exceptions.UnsuspensionTimeLimitExceeded:
        raise api_errors.ForbiddenError({"code": "UNSUSPENSION_LIMIT_REACHED"})

    api.unsuspend_account(user, actor=user, send_email=True)
