from dataclasses import asdict
from datetime import datetime
import logging

from flask import request

from pcapi import settings
from pcapi.connectors import api_recaptcha
from pcapi.connectors import user_profiling
from pcapi.core.fraud import api as fraud_api
from pcapi.core.logging import get_or_set_correlation_id
from pcapi.core.offers.exceptions import FileSizeExceeded
from pcapi.core.users import api
from pcapi.core.users import constants
from pcapi.core.users import exceptions
from pcapi.core.users.external import update_external_user
from pcapi.core.users.models import NotificationSubscriptions
from pcapi.core.users.models import User
from pcapi.models import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.repository.user_queries import find_user_by_email
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
    if body.subscriptions is not None:
        user.notificationSubscriptions = asdict(
            NotificationSubscriptions(
                marketing_email=body.subscriptions.marketing_email, marketing_push=body.subscriptions.marketing_push
            )
        )
    repository.save(user)
    update_external_user(user)

    return serializers.UserProfileResponse.from_orm(user)


@blueprint.native_v1.route("/beneficiary_information", methods=["PATCH"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_user_required
def update_beneficiary_mandatory_information(user: User, body: serializers.BeneficiaryInformationUpdateRequest) -> None:
    api.update_beneficiary_mandatory_information(
        user=user,
        address=body.address,
        city=body.city,
        postal_code=body.postal_code,
        activity=body.activity,
        phone_number=body.phone,
    )


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

    if not FeatureToggle.WHOLE_FRANCE_OPENING.is_active() and not body.postal_code:
        raise ApiErrors(errors={"postalCode": ["Ce champ est obligatoire"]})
    try:
        api.create_account(
            email=body.email,
            password=body.password,
            birthdate=body.birthdate,
            marketing_email_subscription=body.marketing_email_subscription,
            is_email_validated=False,
            postal_code=body.postal_code,
            apps_flyer_user_id=body.apps_flyer_user_id,
            apps_flyer_platform=body.apps_flyer_platform,
        )
    except exceptions.UserAlreadyExistsException:
        user = find_user_by_email(body.email)
        if not user.isEmailValidated:
            user.setPassword(body.password)
            repository.save(user)
            api.delete_all_users_tokens(user)
            try:
                api.request_email_confirmation(user)
            except exceptions.EmailNotSent:
                raise ApiErrors({"email": ["L'email n'a pas pu être envoyé"]})
        else:
            try:
                api.request_password_reset(user)
            except exceptions.EmailNotSent:
                raise ApiErrors({"email": ["L'email n'a pas pu être envoyé"]})
    except exceptions.UnderAgeUserException:
        raise ApiErrors({"dateOfBirth": "The birthdate is invalid"})


@blueprint.native_v1.route("/account/has_completed_id_check", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_user_required
def has_completed_id_check(user: User) -> None:
    user.hasCompletedIdCheck = True
    repository.save(user)
    update_external_user(user)


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


@blueprint.native_v1.route("/id_check_token", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.GetIdCheckTokenResponse)
@authenticated_user_required
def get_id_check_token(user: User) -> serializers.GetIdCheckTokenResponse:
    if not user.is_eligible or user.isBeneficiary:
        raise ApiErrors({"code": "USER_NOT_ELIGIBLE"})
    try:
        id_check_token = api.create_id_check_token(user)
        return serializers.GetIdCheckTokenResponse(
            token=id_check_token.value if id_check_token else None,
            token_timestamp=id_check_token.expirationDate if id_check_token else None,
        )
    except exceptions.IdCheckTokenLimitReached:
        message = f"Tu as fait trop de demandes pour le moment, réessaye dans {settings.ID_CHECK_TOKEN_LIFE_TIME_HOURS} heures"
        raise ApiErrors(
            {"code": "TOO_MANY_ID_CHECK_TOKEN", "message": message},
            status_code=400,
        )
    except exceptions.IdCheckAlreadyCompleted:
        raise ApiErrors(
            {"code": "ID_CHECK_ALREADY_COMPLETED", "message": "Tu as déjà déposé un dossier, il est en cours d'étude."},
            status_code=400,
        )


@blueprint.native_v1.route("/identity_document", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_user_required
def upload_identity_document(
    user: User,
    form: serializers.UploadIdentityDocumentRequest,
) -> None:
    if not user.is_eligible:
        raise ApiErrors({"code": "USER_NOT_ELIGIBLE"})
    try:
        token = api.validate_token(user.id, form.token)
        image = form.get_image_as_bytes(request)
        api.asynchronous_identity_document_verification(image, user.email)
        token.isUsed = True
        repository.save(token)
        return
    except exceptions.ExpiredCode:
        raise ApiErrors(
            {"code": "EXPIRED_TOKEN", "message": "Token expiré"},
            status_code=400,
        )
    except exceptions.NotValidCode:
        raise ApiErrors(
            {"code": "INVALID_TOKEN", "message": "Token invalide"},
            status_code=400,
        )
    except FileSizeExceeded:
        raise ApiErrors(
            {"code": "FILE_SIZE_EXCEEDED", "message": "L'image envoyée dépasse 10Mo"},
            status_code=400,
        )
    except (exceptions.IdentityDocumentUploadException, exceptions.CloudTaskCreationException):
        raise ApiErrors({"code": "SERVICE_UNAVAILABLE", "message": "Token invalide"}, status_code=503)


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
    except (exceptions.UserWithoutPhoneNumberException, exceptions.PhoneAlreadyExists, exceptions.InvalidPhoneNumber):
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


@blueprint.native_v1.route("/user_profiling", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_user_required
def profiling_fraud_score(user: User, body: serializers.UserProfilingFraudRequest) -> None:
    handler = user_profiling.UserProfilingClient()

    try:
        profiling_infos = handler.get_user_profiling_fraud_data(
            session_id=body.session_id,
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
            agent_type=user_profiling.AgentType.AGENT_MOBILE,
        )
    except user_profiling.BaseUserProfilingException:
        logger.exception("Error while retrieving user profiling infos", exc_info=True)
    else:
        logger.info("Success when profiling user: returned userdata %r", profiling_infos.dict())
        fraud_api.create_user_profiling_check(user, profiling_infos)
