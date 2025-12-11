import logging

from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_login import current_user

import pcapi.core.token as token_utils
from pcapi.connectors import api_recaptcha
from pcapi.connectors import google_oauth
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as user_models
from pcapi.core.users import repository as users_repo
from pcapi.core.users.models import User
from pcapi.core.users.password_utils import check_password_strength
from pcapi.core.users.repository import find_user_by_email
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError
from pcapi.models.feature import FeatureToggle
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v1.serialization.authentication import ChangePasswordRequest
from pcapi.routes.native.v1.serialization.authentication import RequestPasswordResetRequest
from pcapi.routes.native.v1.serialization.authentication import ResetPasswordRequest
from pcapi.routes.native.v1.serialization.authentication import ResetPasswordResponse
from pcapi.routes.native.v1.serialization.authentication import ValidateEmailRequest
from pcapi.routes.native.v1.serialization.authentication import ValidateEmailResponse
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.repository import transaction
from pcapi.utils.transaction_manager import atomic
from pcapi.workers import apps_flyer_job

from .. import blueprint
from .serialization import authentication


logger = logging.getLogger(__name__)


@blueprint.native_route("/signin", methods=["POST"])
@spectree_serialize(
    response_model=authentication.SigninResponse,
    on_success_status=200,
    on_error_statuses=[400, 401],
    api=blueprint.api,
)
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

    if user.account_state == user_models.AccountState.ANONYMIZED:
        raise ApiErrors({"code": "ACCOUNT_ANONYMIZED", "general": ["Le compte a été anonymisé"]})

    users_api.save_device_info_and_notify_user(user, body.device_info)

    users_api.update_last_connection_date(user)
    return authentication.SigninResponse(
        access_token=users_api.create_user_access_token(user),
        refresh_token=users_api.create_user_refresh_token(user, body.device_info),
        account_state=user.account_state,
    )


@blueprint.native_route("/refresh_access_token", methods=["POST"])
@jwt_required(refresh=True)
@spectree_serialize(response_model=authentication.RefreshResponse, api=blueprint.api, on_error_statuses=[401])
def refresh() -> authentication.RefreshResponse:
    email = get_jwt_identity()
    user = find_user_by_email(email)
    if not user:
        raise ApiErrors({"email": "unknown"}, status_code=401)
    users_api.update_last_connection_date(user)
    return authentication.RefreshResponse(access_token=users_api.create_user_access_token(user))


@blueprint.native_route("/request_password_reset", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api, on_error_statuses=[400])
def request_password_reset(body: RequestPasswordResetRequest) -> None:
    if FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active():
        try:
            api_recaptcha.check_native_app_recaptcha_token(body.token)
        except api_recaptcha.ReCaptchaException:
            raise ApiErrors({"token": "The given token is not valid"})

    try:
        users_api.check_email_validation_resends_count(body.email)
        users_api.increment_email_resends_count(body.email)
    except users_exceptions.EmailValidationLimitReached:
        raise api_errors.ApiErrors(
            {"message": "Le nombre de tentatives maximal est dépassé.", "code": "TOO_MANY_EMAIL_VALIDATION_RESENDS"},
            status_code=429,
        )

    user = find_user_by_email(body.email)
    users_api.request_password_reset(user)


@blueprint.native_route("/reset_password", methods=["POST"])
@spectree_serialize(
    response_model=ResetPasswordResponse, on_success_status=200, api=blueprint.api, on_error_statuses=[400]
)
@atomic()
def reset_password(body: ResetPasswordRequest) -> ResetPasswordResponse:
    user = users_api.reset_password_with_token(body.new_password, body.reset_password_token)
    return ResetPasswordResponse(
        access_token=users_api.create_user_access_token(user),
        refresh_token=users_api.create_user_refresh_token(user, body.device_info),
    )


@blueprint.native_route("/change_password", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api, on_error_statuses=[400])
@authenticated_and_active_user_required
def change_password(body: ChangePasswordRequest) -> None:
    if current_user.password is None:
        raise ApiErrors({"code": "NO_CURRENT_PASSWORD"})

    try:
        users_repo.check_user_and_credentials(current_user, body.current_password)
    except users_exceptions.InvalidIdentifier:
        raise ApiErrors({"code": "INVALID_PASSWORD", "currentPassword": ["Le mot de passe est incorrect"]})
    except users_exceptions.CredentialsException:
        raise ForbiddenError()

    try:
        check_password_strength("newPassword", body.new_password)
    except ApiErrors:
        raise ApiErrors({"code": "WEAK_PASSWORD", "newPassword": ["Le nouveau mot de passe est trop faible"]})

    current_user.setPassword(body.new_password)
    db.session.add(current_user)
    db.session.commit()


@blueprint.native_route("/validate_email", methods=["POST"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=ValidateEmailResponse)
def validate_email(body: ValidateEmailRequest) -> ValidateEmailResponse:
    try:
        token = token_utils.Token.load_and_check(
            body.email_validation_token, token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION
        )
    except users_exceptions.InvalidToken:
        raise ApiErrors({"token": ["Le token de validation d'email est invalide."]})

    token.expire()
    user = db.session.get(User, token.user_id)
    assert user  # helps mypy

    user.isEmailValidated = True
    db.session.add(user)
    db.session.commit()
    external_attributes_api.update_external_user(user)

    if user.externalIds and "apps_flyer" in user.externalIds:
        apps_flyer_job.log_user_registration_event_job.delay(user.id)

    try:
        dms_subscription_api.try_dms_orphan_adoption(user)
    except Exception:
        logger.exception(
            "An unexpected error occurred while trying to link dms orphan to user", extra={"user_id": user.id}
        )

    response = ValidateEmailResponse(
        access_token=users_api.create_user_access_token(user),
        refresh_token=users_api.create_user_refresh_token(user, body.device_info),
    )

    return response


@blueprint.native_route("/oauth/state", methods=["GET"])
@spectree_serialize(response_model=authentication.OauthStateResponse, on_success_status=200, api=blueprint.api)
def google_oauth_state() -> authentication.OauthStateResponse:
    encoded_oauth_state_token = users_api.create_oauth_state_token()
    return authentication.OauthStateResponse(oauth_state_token=encoded_oauth_state_token)


@blueprint.native_route("/oauth/google/authorize", methods=["POST"])
@spectree_serialize(
    response_model=authentication.SigninResponse,
    on_success_status=200,
    on_error_statuses=[400, 401],
    api=blueprint.api,
)
def google_auth(body: authentication.GoogleSigninRequest) -> authentication.SigninResponse:
    try:
        oauth_state_token = token_utils.UUIDToken.load_and_check(
            body.oauth_state_token, token_utils.TokenType.OAUTH_STATE
        )
    except (users_exceptions.ExpiredToken, users_exceptions.InvalidToken) as e:
        raise ApiErrors(
            {
                "code": "SSO_LOGIN_TIMEOUT",
                "general": ["La demande de connexion a mis trop de temps."],
            },
            status_code=400,
        ) from e
    oauth_state_token.expire()

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
            "Successful SSO authentication but no matching email found, sending account creation token",
            extra={
                "identifier": email,
                "sso_provider": "google",
                "sso_user_id": sso_user_id,
                "user": None,
                "avoid_current_user": True,
                "success": True,
            },
            technical_message_id="users.login.sso.google",
        )
        encoded_account_creation_token = users_api.create_account_creation_token(google_user)
        # the frontends (web, ios & android app) will handle this error and redirect to the account creation form
        raise ApiErrors(
            {
                "code": "SSO_EMAIL_NOT_FOUND",
                "accountCreationToken": encoded_account_creation_token,
                "email": email,
                "general": [f"Aucun compte pass Culture lié à {email} n'a été trouvé"],
            },
            status_code=401,
        )

    user_ssos = user.single_sign_ons if user else []
    user_has_another_google_account_linked = user_ssos and sso_user_id not in [sso.ssoUserId for sso in user_ssos]
    if user_has_another_google_account_linked:
        raise ApiErrors(
            {
                "code": "SSO_DUPLICATE_GOOGLE_ACCOUNT",
                "general": ["Un autre compte Google est déjà associé à ce compte."],
            }
        )

    if user.account_state.is_deleted:
        raise ApiErrors({"code": "SSO_ACCOUNT_DELETED", "general": ["Le compte a été supprimé"]})

    if user.account_state == user_models.AccountState.ANONYMIZED:
        raise ApiErrors({"code": "SSO_ACCOUNT_ANONYMIZED", "general": ["Le compte a été anonymisé"]})

    if not google_user.email_verified:
        raise ApiErrors({"code": "SSO_EMAIL_NOT_VALIDATED", "general": ["L'email n'a pas été validé."]})

    with transaction():
        if not user.isEmailValidated:
            # An account registered with a password and with its email not validated is a symptom
            # of an account pre-hijacking attack waiting for an email validation. To prevent this
            # we disable the email + password login when a SSO is enabled.
            user.password = None
            user.isEmailValidated = True

        if not single_sign_on:
            single_sign_on = users_repo.create_single_sign_on(user, "google", sso_user_id)
            db.session.add(single_sign_on)

    users_api.save_device_info_and_notify_user(user, body.device_info)

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
        refresh_token=users_api.create_user_refresh_token(user, body.device_info),
        account_state=user.account_state,
    )
