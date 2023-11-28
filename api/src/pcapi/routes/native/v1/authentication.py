import logging

from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

from pcapi.connectors import api_recaptcha
from pcapi.connectors import google_oauth
from pcapi.core.external.attributes import api as external_attributes_api
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.subscription.dms import api as dms_subscription_api
import pcapi.core.token as token_utils
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as user_models
from pcapi.core.users import repository as users_repo
from pcapi.core.users.models import User
from pcapi.core.users.repository import find_user_by_email
from pcapi.domain.password import check_password_strength
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v1.serialization.authentication import ChangePasswordRequest
from pcapi.routes.native.v1.serialization.authentication import RequestPasswordResetRequest
from pcapi.routes.native.v1.serialization.authentication import ResetPasswordRequest
from pcapi.routes.native.v1.serialization.authentication import ResetPasswordResponse
from pcapi.routes.native.v1.serialization.authentication import ValidateEmailRequest
from pcapi.routes.native.v1.serialization.authentication import ValidateEmailResponse
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.feature import feature_required
from pcapi.utils.rate_limiting import email_rate_limiter
from pcapi.utils.rate_limiting import ip_rate_limiter

from . import blueprint
from .serialization import authentication


logger = logging.getLogger(__name__)

MAX_SUSPICIOUS_LOGIN_EMAILS = 5


@blueprint.native_v1.route("/signin", methods=["POST"])
@spectree_serialize(
    response_model=authentication.SigninResponse,
    on_success_status=200,
    on_error_statuses=[400, 401],
    api=blueprint.api,
)
@email_rate_limiter()
@ip_rate_limiter()
def signin(body: authentication.SigninRequest) -> authentication.SigninResponse:
    if FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active():
        try:
            api_recaptcha.check_native_app_recaptcha_token(body.token)
        except (api_recaptcha.ReCaptchaException, api_recaptcha.InvalidRecaptchaTokenException):
            raise api_errors.ApiErrors({"token": "Le token est invalide"}, 401)
    try:
        user = users_repo.get_user_with_credentials(body.identifier, body.password, allow_inactive=True)
    except users_exceptions.UnvalidatedAccount as exc:
        raise ApiErrors({"code": "EMAIL_NOT_VALIDATED", "general": ["L'email n'a pas été validé."]}) from exc
    except users_exceptions.CredentialsException as exc:
        raise ApiErrors({"general": ["Identifiant ou Mot de passe incorrect"]}) from exc

    if user.account_state.is_deleted:
        raise ApiErrors({"code": "ACCOUNT_DELETED", "general": ["Le compte a été supprimé"]})

    if FeatureToggle.WIP_ENABLE_TRUSTED_DEVICE.is_active():
        login_history = None
        if body.device_info is not None:
            if users_api.should_save_login_device_as_trusted_device(body.device_info, user):
                users_api.save_trusted_device(body.device_info, user)

            login_history = users_api.update_login_device_history(body.device_info, user)

        should_send_suspicious_login_email = (
            (user.is_active or user.is_account_suspended_upon_user_request)
            and not users_api.is_login_device_a_trusted_device(body.device_info, user)
            and FeatureToggle.WIP_ENABLE_SUSPICIOUS_EMAIL_SEND.is_active()
            and len(users_api.get_recent_suspicious_logins(user)) <= MAX_SUSPICIOUS_LOGIN_EMAILS
        )

        if should_send_suspicious_login_email:
            account_suspension_token = users_api.create_suspicious_login_email_token(login_history, user.id)
            reset_password_token = users_api.create_reset_password_token(user)
            transactional_mails.send_suspicious_login_email(
                user, login_history, account_suspension_token, reset_password_token
            )

    users_api.update_last_connection_date(user)
    return authentication.SigninResponse(
        access_token=users_api.create_user_access_token(user),
        refresh_token=users_api.create_user_refresh_token(user, body.device_info),
        account_state=user.account_state,
    )


@blueprint.native_v1.route("/refresh_access_token", methods=["POST"])
@jwt_required(refresh=True)
@spectree_serialize(response_model=authentication.RefreshResponse, api=blueprint.api, on_error_statuses=[401])
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
            api_recaptcha.check_native_app_recaptcha_token(body.token)
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
@spectree_serialize(
    response_model=ResetPasswordResponse, on_success_status=200, api=blueprint.api, on_error_statuses=[400]
)
def reset_password(body: ResetPasswordRequest) -> ResetPasswordResponse:
    check_password_strength("newPassword", body.new_password)
    token = None
    try:
        token = token_utils.Token.load_and_check(body.reset_password_token, token_utils.TokenType.RESET_PASSWORD)
        user = user_models.User.query.get(token.user_id)
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
    if token:
        token.expire()
    return ResetPasswordResponse(
        access_token=users_api.create_user_access_token(user),
        refresh_token=users_api.create_user_refresh_token(user, body.device_info),
    )


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
        token = token_utils.Token.load_and_check(body.email_validation_token, token_utils.TokenType.EMAIL_VALIDATION)
    except users_exceptions.InvalidToken:
        raise ApiErrors({"token": ["Le token de validation d'email est invalide."]})

    token.expire()
    user = User.query.get(token.user_id)

    user.isEmailValidated = True
    repository.save(user)
    external_attributes_api.update_external_user(user)

    try:
        dms_subscription_api.try_dms_orphan_adoption(user)
    except Exception:  # pylint: disable=broad-except
        logger.exception(
            "An unexpected error occurred while trying to link dms orphan to user", extra={"user_id": user.id}
        )

    response = ValidateEmailResponse(
        access_token=users_api.create_user_access_token(user),
        refresh_token=users_api.create_user_refresh_token(user, body.device_info),
    )

    return response


@blueprint.native_v1.route("/oauth/google/authorize", methods=["POST"])
@spectree_serialize(
    response_model=authentication.SigninResponse,
    on_success_status=200,
    on_error_statuses=[400, 401],
    api=blueprint.api,
)
@ip_rate_limiter()
@feature_required(FeatureToggle.WIP_ENABLE_GOOGLE_SSO)
def google_auth(body: authentication.GoogleSigninRequest) -> authentication.SigninResponse:
    google_user = google_oauth.get_google_user(body.authorization_code)
    email = google_user.email
    sso_user_id = google_user.sub

    single_sign_on = users_repo.get_single_sign_on("google", sso_user_id)
    if not single_sign_on:
        user = users_repo.find_user_by_email(email)
    else:
        user = single_sign_on.user

    if not user:
        logger.info(
            "Failed authentication attempt",
            extra={
                "identifier": email,
                "sso_provider": "google",
                "sso_user_id": sso_user_id,
                "user": "not found",
                "avoid_current_user": True,
                "success": True,
            },
            technical_message_id="users.login.sso.google",
        )
        raise ApiErrors({"email": "unknown"}, status_code=401)

    user_ssos = user.single_sign_ons if user else []
    user_has_another_google_account_linked = user_ssos and sso_user_id not in [sso.ssoUserId for sso in user_ssos]
    if user_has_another_google_account_linked:
        raise ApiErrors(
            {"code": "DUPLICATE_GOOGLE_ACCOUNT", "general": ["Un autre compte Google est déjà associé à ce compte."]}
        )

    if user.account_state.is_deleted:
        raise ApiErrors({"code": "ACCOUNT_DELETED", "general": ["Le compte a été supprimé"]})

    if not user.isValidated or not user.isEmailValidated or not google_user.email_verified:
        raise ApiErrors({"code": "EMAIL_NOT_VALIDATED", "general": ["L'email n'a pas été validé."]})

    if not single_sign_on:
        with transaction():
            single_sign_on = users_repo.create_single_sign_on(user, "google", sso_user_id)
            db.session.add(single_sign_on)

    users_api.update_last_connection_date(user)
    logger.info(
        "Successful authentication attempt",
        extra={
            "identifier": email,
            "user": user.id,
            "sso_provider": "google",
            "sso_user_id": sso_user_id,
            "avoid_current_user": True,
            "success": True,
        },
        technical_message_id="users.login.sso.google",
    )
    return authentication.SigninResponse(
        access_token=users_api.create_user_access_token(user),
        refresh_token=users_api.create_user_refresh_token(user, device_info=None),
        account_state=user.account_state,
    )
