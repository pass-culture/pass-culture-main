from datetime import datetime
import logging
import uuid

from flask import request
from jwt import InvalidTokenError
import pydantic

from pcapi.connectors import api_recaptcha
from pcapi.connectors import user_profiling
from pcapi.connectors.beneficiaries import exceptions as beneficiaries_exceptions
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud.ubble import api as ubble_fraud_api
from pcapi.core.logging import get_or_set_correlation_id
from pcapi.core.mails.transactional.users.delete_account import send_user_request_to_delete_account_reception_email
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.users import api
from pcapi.core.users import constants
from pcapi.core.users import email as email_api
from pcapi.core.users import exceptions
from pcapi.core.users.external import update_external_user
from pcapi.core.users.models import User
from pcapi.core.users.repository import find_user_by_email
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.repository import transaction
from pcapi.routes.native.security import authenticated_user_required
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import account as serializers


logger = logging.getLogger(__name__)


@blueprint.native_v1.route("/me", methods=["GET"])
@spectree_serialize(
    response_model=serializers.UserProfileResponse,
    on_success_status=200,
    api=blueprint.api,
)  # type: ignore
@authenticated_user_required
def get_user_profile(user: User) -> serializers.UserProfileResponse:
    return serializers.UserProfileResponse.from_orm(user)


@blueprint.native_v1.route("/profile", methods=["POST"])
@spectree_serialize(
    response_model=serializers.UserProfileResponse,
    on_success_status=200,
    api=blueprint.api,
)  # type: ignore
@authenticated_user_required
def update_user_profile(user: User, body: serializers.UserProfileUpdateRequest) -> serializers.UserProfileResponse:
    api.update_notification_subscription(user, body.subscriptions)
    update_external_user(user)
    return serializers.UserProfileResponse.from_orm(user)


@blueprint.native_v1.route("/reset_recredit_amount_to_show", methods=["POST"])
@spectree_serialize(
    on_success_status=200,
    api=blueprint.api,
)  # type: ignore
@authenticated_user_required
def reset_recredit_amount_to_show(user: User) -> None:
    api.reset_recredit_amount_to_show(user)

    return serializers.UserProfileResponse.from_orm(user)


@blueprint.native_v1.route("/profile/update_email", methods=["POST"])
@spectree_serialize(
    on_success_status=204,
    api=blueprint.api,
)  # type: ignore
@authenticated_user_required
def update_user_email(user: User, body: serializers.UserProfileEmailUpdate) -> None:
    try:
        email_api.request_email_update(user, body.email, body.password)
    except exceptions.EmailUpdateTokenExists:
        raise ApiErrors(
            {"code": "TOKEN_EXISTS", "message": "Une demande de modification d'adresse e-mail est déjà en cours"},
            status_code=400,
        )
    except exceptions.EmailUpdateInvalidPassword:
        raise ApiErrors(
            {"code": "INVALID_PASSWORD", "message": "Mot de passe invalide"},
            status_code=400,
        )
    except exceptions.InvalidEmailError:
        raise ApiErrors(
            {"code": "INVALID_EMAIL", "message": "Adresse email invalide"},
            status_code=400,
        )
    except exceptions.EmailUpdateLimitReached:
        raise ApiErrors(
            {"code": "EMAIL_UPDATE_ATTEMPTS_LIMIT", "message": "Trop de tentatives"},
            status_code=400,
        )
    except exceptions.EmailExistsError:
        # Returning an error message might help the end client find
        # existing email addresses.
        pass


@blueprint.native_v1.route("/profile/validate_email", methods=["PUT"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
def validate_user_email(body: serializers.ChangeBeneficiaryEmailBody) -> None:
    try:
        payload = serializers.ChangeEmailTokenContent.from_token(body.token)
        api.change_user_email(current_email=payload.current_email, new_email=payload.new_email)
    except pydantic.ValidationError:
        raise ApiErrors(
            {"code": "INVALID_EMAIL", "message": "Adresse email invalide"},
            status_code=400,
        )
    except InvalidTokenError:
        raise ApiErrors(
            {"code": "INVALID_TOKEN", "message": "Token invalide"},
            status_code=400,
        )
    except exceptions.EmailExistsError:
        # Returning an error message might help the end client find
        # existing email addresses.
        pass


@blueprint.native_v1.route("/profile/token_expiration", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=serializers.UpdateEmailTokenExpiration)
@authenticated_user_required
def get_email_update_token_expiration_date(user: User) -> serializers.UpdateEmailTokenExpiration:
    return serializers.UpdateEmailTokenExpiration(expiration=email_api.get_active_token_expiration(user))


@blueprint.native_v1.route("/me/cultural_survey", methods=["POST"])
@spectree_serialize(
    on_success_status=204,
    on_error_statuses=[400],
    api=blueprint.api,
)  # type: ignore
@authenticated_user_required
def update_cultural_survey(user: User, body: serializers.CulturalSurveyRequest) -> None:
    with transaction():
        if not body.needs_to_fill_cultural_survey:
            user.needsToFillCulturalSurvey = False
        if body.cultural_survey_id:
            logger.info("User %s updated cultural survey", user.id, extra={"actor": user.id})
            user.culturalSurveyId = body.cultural_survey_id
            user.culturalSurveyFilledDate = datetime.now()
    return


@blueprint.native_v1.route("/account", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api, on_error_statuses=[400])
def create_account(body: serializers.AccountRequest) -> None:
    if FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active():
        try:
            api_recaptcha.check_native_app_recaptcha_token(body.token)
        except api_recaptcha.ReCaptchaException:
            raise ApiErrors({"token": "The given token is not invalid"})

    try:
        api.create_account(
            email=body.email,
            password=body.password,
            birthdate=body.birthdate,
            marketing_email_subscription=body.marketing_email_subscription,
            is_email_validated=False,
            apps_flyer_user_id=body.apps_flyer_user_id,
            apps_flyer_platform=body.apps_flyer_platform,
        )
    except exceptions.UserAlreadyExistsException:
        user = find_user_by_email(body.email)
        if not user.isEmailValidated:
            try:
                api.initialize_account(
                    user,
                    body.password,
                    apps_flyer_user_id=body.apps_flyer_user_id,
                    apps_flyer_platform=body.apps_flyer_platform,
                )
            except exceptions.EmailNotSent:
                raise ApiErrors({"email": ["L'email n'a pas pu être envoyé"]})
        else:
            try:
                api.request_password_reset(user)
            except exceptions.EmailNotSent:
                raise ApiErrors({"email": ["L'email n'a pas pu être envoyé"]})
    except exceptions.UnderAgeUserException:
        raise ApiErrors({"dateOfBirth": "The birthdate is invalid"})


@blueprint.native_v1.route("/resend_email_validation", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
def resend_email_validation(body: serializers.ResendEmailValidationRequest) -> None:
    user = find_user_by_email(body.email)
    if not user or not user.isActive:
        return
    try:
        if user.isEmailValidated:
            api.request_password_reset(user)
        else:
            api.request_email_confirmation(user)
    except exceptions.EmailNotSent:
        raise ApiErrors(
            {"code": "EMAIL_NOT_SENT", "general": ["L'email n'a pas pu être envoyé"]},
            status_code=400,
        )


@blueprint.native_v1.route("/send_phone_validation_code", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_user_required
def send_phone_validation_code(user: User, body: serializers.SendPhoneValidationRequest) -> None:
    try:
        if body.phoneNumber:
            api.change_user_phone_number(user, body.phoneNumber)

        api.send_phone_validation_code(user)

    except exceptions.SMSSendingLimitReached:
        raise ApiErrors(
            {"code": "TOO_MANY_SMS_SENT", "message": "Nombre de tentatives maximal dépassé"},
            status_code=400,
        )
    except exceptions.UserPhoneNumberAlreadyValidated:
        raise ApiErrors(
            {"message": "Le numéro de téléphone est déjà validé", "code": "PHONE_NUMBER_ALREADY_VALIDATED"},
            status_code=400,
        )
    except (exceptions.PhoneAlreadyExists, exceptions.InvalidPhoneNumber):
        raise ApiErrors(
            {"message": "Le numéro de téléphone est invalide", "code": "INVALID_PHONE_NUMBER"}, status_code=400
        )
    except exceptions.PhoneVerificationException:
        raise ApiErrors({"message": "L'envoi du code a échoué", "code": "CODE_SENDING_FAILURE"}, status_code=400)


@blueprint.native_v1.route("/validate_phone_number", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_user_required
def validate_phone_number(user: User, body: serializers.ValidatePhoneNumberRequest) -> None:
    with transaction():
        try:
            api.validate_phone_number_and_activate_user(user, body.code)
        except exceptions.PhoneValidationAttemptsLimitReached:
            raise ApiErrors(
                {"message": "Le nombre de tentatives maximal est dépassé", "code": "TOO_MANY_VALIDATION_ATTEMPTS"},
                status_code=400,
            )
        except exceptions.ExpiredCode:
            raise ApiErrors({"message": "Le code saisi a expiré", "code": "EXPIRED_VALIDATION_CODE"}, status_code=400)
        except exceptions.NotValidCode:
            raise ApiErrors({"message": "Le code est invalide", "code": "INVALID_VALIDATION_CODE"}, status_code=400)
        except exceptions.InvalidPhoneNumber:
            raise ApiErrors(
                {"message": "Le numéro de téléphone est invalide", "code": "INVALID_PHONE_NUMBER"}, status_code=400
            )
        except exceptions.PhoneVerificationException:
            raise ApiErrors({"message": "L'envoi du code a échoué", "code": "CODE_SENDING_FAILURE"}, status_code=400)


@blueprint.native_v1.route("/account/suspend", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_user_required
def suspend_account(user: User) -> None:
    api.suspend_account(user, constants.SuspensionReason.UPON_USER_REQUEST, actor=user)
    send_user_request_to_delete_account_reception_email(user)


@blueprint.native_v1.route("/user_profiling", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_user_required
def profiling_fraud_score(user: User, body: serializers.UserProfilingFraudRequest) -> None:
    handler = user_profiling.UserProfilingClient()

    # User Profiling step must be after Phone Validation
    if not user.is_phone_validated and FeatureToggle.ENABLE_PHONE_VALIDATION.is_active():
        raise ApiErrors(
            {"message": "Le numéro de téléphone est n'a pas été validé", "code": "MISSING_PHONE_VALIDATION"},
            status_code=400,
        )

    try:
        profiling_infos = handler.get_user_profiling_fraud_data(
            session_id=body.sessionId,
            user_id=user.id,
            user_email=user.email,
            birth_date=user.dateOfBirth.date() if user.dateOfBirth else None,
            phone_number=user.phoneNumber,
            workflow_type=user_profiling.WorkflowType.BENEFICIARY_VALIDATION,
            # depends on loadbalancer configuration
            ip_address=request.headers.get("X-Forwarded-For"),
            line_of_business=user_profiling.LineOfBusiness.B2C,
            # Insert request unique identifier
            transaction_id=get_or_set_correlation_id(),
            agent_type=body.agentType,
        )
    except user_profiling.BaseUserProfilingException:
        logger.exception("Error while retrieving user profiling infos", exc_info=True)
    else:
        logger.info(
            "Success when profiling user: returned userdata %r",
            profiling_infos.dict(),
            extra={"sessionId": body.sessionId},
        )
        fraud_api.on_user_profiling_result(user, profiling_infos)
        subscription_api.activate_beneficiary_if_no_missing_step(user, False)


@blueprint.native_v1.route("/user_profiling/session_id", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.UserProfilingSessionIdResponse)
@authenticated_user_required
def profiling_session_id(user: User) -> serializers.UserProfilingSessionIdResponse:
    """
    Generate a unique hash which will be used as an identifier for user profiling
    """
    session_id = str(uuid.uuid4())
    return serializers.UserProfilingSessionIdResponse(sessionId=session_id)


@blueprint.native_v1.route("/ubble_identification", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=serializers.IdentificationSessionResponse)
@authenticated_user_required
def start_identification_session(
    user: User, body: serializers.IdentificationSessionRequest
) -> serializers.IdentificationSessionResponse:

    if user.eligibility is None:
        raise ApiErrors(
            {"code": "IDCHECK_NOT_ELIGIBLE", "message": "Non éligible à un crédit"},
            status_code=400,
        )

    if not ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility):
        raise ApiErrors(
            {"code": "IDCHECK_ALREADY_PROCESSED", "message": "Une identification a déjà été traitée"},
            status_code=400,
        )

    fraud_check = ubble_fraud_api.get_restartable_identity_checks(user)
    if fraud_check:
        return serializers.IdentificationSessionResponse(identificationUrl=fraud_check.source_data().identification_url)

    try:
        identification_url = ubble_subscription_api.start_ubble_workflow(user, body.redirectUrl)
        return serializers.IdentificationSessionResponse(identificationUrl=identification_url)

    except beneficiaries_exceptions.IdentificationServiceUnavailable:
        raise ApiErrors(
            {"code": "IDCHECK_SERVICE_UNAVAILABLE", "message": "Le service d'identification n'est pas joignable"},
            status_code=503,
        )

    except beneficiaries_exceptions.IdentificationServiceError:
        raise ApiErrors(
            {
                "code": "IDCHECK_SERVICE_ERROR",
                "message": "Une erreur s'est produite à l'appel du service d'identification",
            },
            status_code=500,
        )
