from dataclasses import asdict
from datetime import datetime
import logging

from pcapi.connectors import api_recaptcha
from pcapi.core.users import api
from pcapi.core.users import exceptions
from pcapi.core.users.models import NotificationSubscriptions
from pcapi.core.users.models import User
from pcapi.models import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.repository.user_queries import find_user_by_email
from pcapi.routes.native.security import authenticated_user_required
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)
from pcapi.workers.push_notification_job import update_user_attributes_job

from . import blueprint
from .serialization import account as serializers


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
    update_user_attributes_job.delay(user.id)

    return serializers.UserProfileResponse.from_orm(user)


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
    if feature_queries.is_active(FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA):
        try:
            api_recaptcha.check_native_app_recaptcha_token(body.token)
        except api_recaptcha.ReCaptchaException:
            raise ApiErrors({"token": "The given token is not invalid"})

    if not feature_queries.is_active(FeatureToggle.WHOLE_FRANCE_OPENING) and not body.postal_code:
        raise ApiErrors(errors={"postalCode": ["Ce champ est obligatoire"]})
    try:
        api.create_account(
            email=body.email,
            password=body.password,
            birthdate=body.birthdate,
            marketing_email_subscription=body.marketing_email_subscription,
            is_email_validated=False,
            postal_code=body.postal_code,
        )
    except exceptions.UserAlreadyExistsException:
        try:
            user = find_user_by_email(body.email)
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


@blueprint.native_v1.route("/id_check_token", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.GetIdCheckTokenResponse)
@authenticated_user_required
def get_id_check_token(user: User) -> serializers.GetIdCheckTokenResponse:
    id_check_token = api.create_id_check_token(user)

    return serializers.GetIdCheckTokenResponse(token=id_check_token.value if id_check_token else None)


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
    except exceptions.UserWithoutPhoneNumberException:
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
            api.validate_phone_number(user, body.code)
        except exceptions.PhoneValidationAttemptsLimitReached:
            raise ApiErrors(
                {"message": "Le nombre de tentatives maximal est dépassé", "code": "TOO_MANY_VALIDATION_ATTEMPTS"},
                status_code=400,
            )
        except exceptions.ExpiredCode:
            raise ApiErrors({"message": "Le code saisi a expiré", "code": "EXPIRED_VALIDATION_CODE"}, status_code=400)
        except exceptions.NotValidCode:
            raise ApiErrors({"message": "Le code est invalide", "code": "INVALID_VALIDATION_CODE"}, status_code=400)
