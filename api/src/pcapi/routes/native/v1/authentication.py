import logging

from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

from pcapi.connectors import api_recaptcha
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import external as users_external
from pcapi.core.users import repository as users_repo
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.core.users.repository import find_user_by_email
from pcapi.domain.password import check_password_strength
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v1.serialization.authentication import ChangePasswordRequest
from pcapi.routes.native.v1.serialization.authentication import RequestPasswordResetRequest
from pcapi.routes.native.v1.serialization.authentication import ResetPasswordRequest
from pcapi.routes.native.v1.serialization.authentication import ValidateEmailRequest
from pcapi.routes.native.v1.serialization.authentication import ValidateEmailResponse
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rate_limiting import email_rate_limiter
from pcapi.utils.rate_limiting import ip_rate_limiter

from . import blueprint
from .serialization import authentication


logger = logging.getLogger(__name__)


@blueprint.native_v1.route("/signin", methods=["POST"])
@spectree_serialize(
    response_model=authentication.SigninResponse,
    on_success_status=200,
    api=blueprint.api,
)
@email_rate_limiter()
@ip_rate_limiter()
def signin(body: authentication.SigninRequest) -> authentication.SigninResponse:
    try:
        allow_inactive = FeatureToggle.ALLOW_ACCOUNT_UNSUSPENSION.is_active()
        user = users_repo.get_user_with_credentials(body.identifier, body.password, allow_inactive=allow_inactive)
    except users_exceptions.UnvalidatedAccount as exc:
        raise ApiErrors({"code": "EMAIL_NOT_VALIDATED", "general": ["L'email n'a pas été validé."]}) from exc
    except users_exceptions.CredentialsException as exc:
        raise ApiErrors({"general": ["Identifiant ou Mot de passe incorrect"]}) from exc

    if user.account_state.is_deleted:
        raise ApiErrors({"code": "ACCOUNT_DELETED", "general": ["Le compte a été supprimé"]})

    users_api.update_last_connection_date(user)
    return authentication.SigninResponse(
        access_token=users_api.create_user_access_token(user),
        refresh_token=create_refresh_token(identity=user.email),
        account_state=user.account_state,
    )


@blueprint.native_v1.route("/refresh_access_token", methods=["POST"])
@jwt_required(refresh=True)
@spectree_serialize(response_model=authentication.RefreshResponse, api=blueprint.api)
def refresh() -> authentication.RefreshResponse:
    email = get_jwt_identity()
    user = find_user_by_email(email)
    if not user:
        raise ApiErrors({"email": "unknown"}, status_code=401)
    users_api.update_last_connection_date(user)
    return authentication.RefreshResponse(access_token=users_api.create_user_access_token(user))


@blueprint.native_v1.route("/request_password_reset", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api, on_error_statuses=[400])
def request_password_reset(body: RequestPasswordResetRequest) -> None:
    if FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active():
        try:
            api_recaptcha.check_native_app_recaptcha_token(body.token)  # type: ignore [arg-type]
        except api_recaptcha.ReCaptchaException:
            raise ApiErrors({"token": "The given token is not valid"})
    user = find_user_by_email(body.email)
    try:
        users_api.request_password_reset(user)
    except users_exceptions.EmailNotSent:
        raise ApiErrors(
            {"email": ["L'email n'a pas pu être envoyé"]},
            status_code=400,
        )


@blueprint.native_v1.route("/reset_password", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api, on_error_statuses=[400])
def reset_password(body: ResetPasswordRequest) -> None:
    check_password_strength("newPassword", body.new_password)

    try:
        user = users_repo.get_user_with_valid_token(body.reset_password_token, [TokenType.RESET_PASSWORD])
    except users_exceptions.InvalidToken:
        raise ApiErrors({"token": ["Le token de changement de mot de passe est invalide."]})

    user.setPassword(body.new_password)

    if not user.isEmailValidated:
        user.isEmailValidated = True
        try:
            dms_subscription_api.try_dms_orphan_adoption(user)
        except Exception:  # pylint: disable=broad-except
            logger.exception(
                "An unexpected error occurred while trying to link dms orphan to user", extra={"user_id": user.id}
            )

    repository.save(user)


@blueprint.native_v1.route("/change_password", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api, on_error_statuses=[400])
@authenticated_and_active_user_required
def change_password(user: User, body: ChangePasswordRequest) -> None:
    try:
        users_repo.check_user_and_credentials(user, body.current_password)
    except users_exceptions.InvalidIdentifier:
        raise ApiErrors({"code": "INVALID_PASSWORD", "currentPassword": ["Le mot de passe est incorrect"]})
    except users_exceptions.CredentialsException:
        raise ForbiddenError()

    try:
        check_password_strength("newPassword", body.new_password)
    except ApiErrors:
        raise ApiErrors({"code": "WEAK_PASSWORD", "newPassword": ["Le nouveau mot de passe est trop faible"]})

    user.setPassword(body.new_password)
    repository.save(user)


@blueprint.native_v1.route("/validate_email", methods=["POST"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=ValidateEmailResponse)
def validate_email(body: ValidateEmailRequest) -> ValidateEmailResponse:
    try:
        user = users_repo.get_user_with_valid_token(
            body.email_validation_token, [TokenType.EMAIL_VALIDATION], use_token=True
        )
    except users_exceptions.InvalidToken as exception:
        if isinstance(exception, users_exceptions.ExpiredToken):
            users_api.request_email_confirmation(exception.user)
        raise ApiErrors({"token": ["Le token de validation d'email est invalide."]})

    user.isEmailValidated = True
    repository.save(user)
    users_external.update_external_user(user)

    try:
        dms_subscription_api.try_dms_orphan_adoption(user)
    except Exception:  # pylint: disable=broad-except
        logger.exception(
            "An unexpected error occurred while trying to link dms orphan to user", extra={"user_id": user.id}
        )

    response = ValidateEmailResponse(
        access_token=users_api.create_user_access_token(user),
        refresh_token=create_refresh_token(identity=user.email),
    )

    return response
