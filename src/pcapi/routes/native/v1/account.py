from dataclasses import asdict
from datetime import datetime

from pcapi.connectors import api_recaptcha
from pcapi.core.users import api
from pcapi.core.users import exceptions
from pcapi.core.users.models import User
from pcapi.models import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.repository.user_queries import find_user_by_email
from pcapi.routes.native.security import authenticated_user_required
from pcapi.serialization.decorator import spectree_serialize

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
    if body.hasAllowedRecommendations is not None:
        user.hasAllowedRecommendations = body.hasAllowedRecommendations
    if body.subscriptions is not None:
        user.notificationSubscriptions = asdict(body.subscriptions)
    repository.save(user)
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
            if user.culturalSurveyId:
                raise ApiErrors({"culturalSurveyId": "L'utilisateur a déjà rempli le formulaire"})
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
    try:
        api.create_account(
            email=body.email,
            password=body.password,
            birthdate=body.birthdate,
            has_allowed_recommendations=body.has_allowed_recommendations,
            is_email_validated=False,
        )
    except exceptions.UserAlreadyExistsException:
        user = find_user_by_email(body.email)
        api.request_password_reset(user)
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
