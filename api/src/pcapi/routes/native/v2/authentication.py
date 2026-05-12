import logging

from flask import g
from flask import request
from flask_login import current_user

import pcapi.core.token as token_utils
from pcapi.connectors import api_recaptcha
from pcapi.connectors import apple_oauth
from pcapi.connectors import google_oauth
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as user_models
from pcapi.core.users import repository as users_repo
from pcapi.core.users.sessions import create_user_jwt_tokens
from pcapi.core.users.sessions import refresh_user_jwt_tokens
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.routes.native.security import _raise_forbidden
from pcapi.routes.native.security import authenticated_with_refresh_token
from pcapi.routes.native.v2.serialization import authentication
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.repository import transaction
from pcapi.utils.transaction_manager import atomic

from .. import blueprint


logger = logging.getLogger(__name__)


@blueprint.native_route("/signin", version="v2", methods=["POST"])
@spectree_serialize(
    response_model=authentication.SigninResponseV2,
    on_success_status=200,
    on_error_statuses=[400, 401],
    api=blueprint.api,
)
def signin(body: authentication.SigninRequestV2) -> authentication.SigninResponseV2:
    if FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active():
        try:
            api_recaptcha.check_native_app_recaptcha_token(body.token)
        except (api_recaptcha.ReCaptchaException, api_recaptcha.InvalidRecaptchaTokenException):
            raise ApiErrors({"token": "Le token est invalide"}, 401)
    try:
        user = users_repo.get_user_with_credentials(body.identifier, body.password, allow_inactive=True)
    except users_exceptions.UnvalidatedAccount as exc:
        raise ApiErrors({"code": "EMAIL_NOT_VALIDATED", "general": ["L'email n'a pas été validé."]}) from exc
    except users_exceptions.CredentialsException as exc:
        raise ApiErrors({"general": ["Identifiant ou Mot de passe incorrect"]}) from exc

    if user.account_state.is_deleted or user.account_state == user_models.AccountState.ANONYMIZED:
        raise ApiErrors({"general": ["Identifiant ou Mot de passe incorrect"]})

    users_api.save_device_info_and_notify_user(user, body.device_info)

    users_api.update_last_connection_date(user)
    tokens = create_user_jwt_tokens(
        user=user,
        device_info=body.device_info,
    )
    return authentication.SigninResponseV2(
        access_token=tokens.access,
        refresh_token=tokens.refresh,
        account_state=user.account_state,
    )


@blueprint.native_route("/refresh_access_token", version="v2", methods=["POST"])
@authenticated_with_refresh_token
@spectree_serialize(response_model=authentication.RefreshResponseV2, api=blueprint.api, on_error_statuses=[401])
@atomic()
def refresh(body: authentication.RefreshRequestV2) -> authentication.RefreshResponseV2:
    # TODO rpa : after removing `v1/refresh_access_token` move that code in authenticated_with_refresh_token
    if g.jwt.data.sub.isdigit():  # after 07/2027 this condition will always be True
        native_user_session = (
            db.session.query(user_models.NativeUserSession)
            .filter(user_models.NativeUserSession.refreshToken == g.jwt.data.jti)
            .one_or_none()
        )
        if not native_user_session:
            _raise_forbidden(g.jwt.data.sub)
        assert native_user_session is not None  # helps mypy

        if native_user_session.deviceId and native_user_session.deviceId != body.device_info.device_id:
            # sometime we don't have the deviceId when generating the token but if we do let's check it
            _raise_forbidden(g.jwt.data.sub)

    users_api.update_last_connection_date(current_user)
    tokens = refresh_user_jwt_tokens(
        user=current_user,
        device_info=body.device_info,
    )
    return authentication.RefreshResponseV2(access_token=tokens.access, refresh_token=tokens.refresh)


@blueprint.native_route("/oauth/state", version="v2", methods=["GET"])
@spectree_serialize(response_model=authentication.OauthStateResponseV2, on_success_status=200, api=blueprint.api)
def sso_oauth_state() -> authentication.OauthStateResponseV2:
    encoded_oauth_state_token = users_api.create_oauth_state_token()
    return authentication.OauthStateResponseV2(oauth_state_token=encoded_oauth_state_token)


_SSO_ACCESS_DENIED_ERROR = {
    "code": "SSO_ERROR",
    "general": ["La connexion avec ce compte SSO est refusée. Contacte le support pour plus d'informations."],
}


@blueprint.native_route("/oauth/<string:sso_provider>/authorize", version="v2", methods=["POST"])
@spectree_serialize(
    response_model=authentication.SigninResponseV2,
    on_success_status=200,
    on_error_statuses=[400, 401],
    api=blueprint.api,
)
def sso_authorize(sso_provider: str, body: authentication.OAuthSigninRequestV2) -> authentication.SigninResponseV2:
    if sso_provider not in authentication.SSOProvider:
        raise api_errors.ApiErrors({"error": "Unknown SSO provider"})

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

    is_web = request.headers.get("platform") == "web"
    if sso_provider == "apple":
        try:
            sso_user = apple_oauth.get_apple_user(body.authorization_code, is_web)
        except apple_oauth.AppleSignInException:
            raise ApiErrors({"code": "SSO_ERROR", "general": "L'authentification a échoué"}, status_code=401)
    elif sso_provider == "google":
        sso_user = google_oauth.get_google_user(body.authorization_code, is_web)

    if not sso_user.email_verified:
        logger.warning(
            "SSO access denied: email not verified",
            extra={"sso_provider": sso_provider},
        )
        raise ApiErrors(_SSO_ACCESS_DENIED_ERROR)

    if not sso_user.email:
        raise api_errors.ApiErrors(
            {"code": "EMAIL_MISSING", "general": ["L'email n'a pas pu être récupéré auprès du fournisseur SSO."]}
        )

    email = sso_user.email
    sso_user_id = sso_user.sub
    single_sign_on = users_repo.get_single_sign_on(sso_provider, sso_user_id)
    if not single_sign_on:
        user = users_repo.find_user_by_email(email)
    else:
        user = single_sign_on.user

    if not user:
        logger.info(
            "Successful SSO authentication but no matching email found, sending account creation token",
            extra={"sso_provider": sso_provider, "avoid_current_user": True},
            technical_message_id=f"users.login.sso.{sso_provider}",
        )
        encoded_account_creation_token = users_api.create_account_creation_token(sso_user)
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

    if user.account_state.is_deleted or user.account_state == user_models.AccountState.ANONYMIZED:
        logger.warning(
            "SSO access denied: account state is not allowed",
            extra={"sso_provider": sso_provider, "account_state": user.account_state},
        )
        raise ApiErrors(_SSO_ACCESS_DENIED_ERROR)

    sso_user_id = sso_user.sub
    with transaction():
        if not user.isEmailValidated:
            # An account registered with a password and with its email not validated is a symptom
            # of an account pre-hijacking attack waiting for an email validation. To prevent this
            # we disable the email + password login when a SSO is enabled.
            user.password = None
            user.isEmailValidated = True

        current_provider_sso = None
        user_ssos_for_provider = [sso for sso in user.single_sign_ons if sso.ssoProvider == sso_provider]
        if user_ssos_for_provider:
            current_provider_sso = user_ssos_for_provider[0]
            current_provider_sso.ssoUserId = sso_user.sub
        else:
            current_provider_sso = users_repo.create_single_sign_on(user, sso_provider, sso_user_id)
            db.session.add(current_provider_sso)

    users_api.save_device_info_and_notify_user(user, body.device_info)

    users_api.update_last_connection_date(user)
    logger.info(
        "Successful authentication attempt",
        extra={"sso_provider": sso_provider, "avoid_current_user": True},
        technical_message_id=f"users.login.sso.{sso_provider}",
    )
    tokens = create_user_jwt_tokens(user=user, device_info=body.device_info)
    return authentication.SigninResponseV2(
        access_token=tokens.access,
        refresh_token=tokens.refresh,
        account_state=user.account_state,
    )
