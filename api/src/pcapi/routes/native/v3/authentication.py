import enum
import logging
import secrets
import time

import pydantic
from flask import url_for

from pcapi import settings
from pcapi.connectors import api_recaptcha
from pcapi.core import token as token_utils
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as user_models
from pcapi.core.users import repository as users_repo
from pcapi.core.users.sessions import create_user_jwt_tokens
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.routes.native.v3.serialization import authentication
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.redis import get_redis_client
from pcapi.utils.transaction_manager import atomic

from .. import blueprint


logger = logging.getLogger(__name__)


USER_BAN_REDIS_KEY = "native:user:authantication_forbidden:%s"


class SecondFactor(enum.StrEnum):
    OTP_MAIL = "OTP_MAIL"


class MfaAuthSession(pydantic.BaseModel):
    user_id: int
    expiration: int
    available_second_factor: list[SecondFactor]
    current_step: dict | None
    device_info: authentication.DeviceInfoV3


def _get_mfa_offer(factor: SecondFactor, token: str) -> authentication.MfaOfferV3:
    match factor:
        case SecondFactor.OTP_MAIL:
            return authentication.MfaOfferV3(
                type=factor.value,
                endpoint=url_for(".otp_mail", token=token),
            )
    raise ValueError("unknown second factor %s" % factor)


def _get_available_mfa(user: user_models.User) -> list[SecondFactor]:
    return [SecondFactor.OTP_MAIL]


def _save_auth_session(session: MfaAuthSession) -> str:
    return token_utils.create_token(
        token_type=token_utils.TokenType.NATIVE_AUTH_SESSION,
        at=session.expiration,
        data=session.model_dump(),
    )


def _load_auth_session(token: str, second_factor: SecondFactor) -> MfaAuthSession:
    try:
        data = token_utils.load_token(token_type=token_utils.TokenType.NATIVE_AUTH_SESSION, token=token)
    except users_exceptions.InvalidToken as exc:
        raise ApiErrors({"token": ["Token invalide"]}, status_code=401) from exc

    if not data:
        raise ApiErrors({"token": ["Token invalide"]}, status_code=401)

    session = MfaAuthSession.model_validate(data)

    # check if this factor is available for this session
    if second_factor not in session.available_second_factor:
        _block_user_connection(session.user_id, settings.NATIVE_APP_AUTHENTICATION_BAN_DURATION)
        raise ApiErrors({"token": ["Méthode d'authentification invalide"]}, status_code=401)
    # once a factor has been selected, it is the only one available
    session.available_second_factor = [second_factor]

    # a banned user cannot continue an authentication process
    if _is_user_blocked(session.user_id):
        raise ApiErrors({"token": ["Token invalide"]}, status_code=401)

    return session


def _conclude_authentication(user: user_models.User, device_info: authentication.DeviceInfoV3) -> tuple[str, str]:
    logger.info(
        "Successful authentication attempt",
        extra={
            "identifier": user.email,
            "user": user.id,
            "avoid_current_user": True,
            "success": True,
            "api_version": "v1",
        },
        technical_message_id="users.login",
    )
    users_api.save_device_info_and_notify_user(user, device_info)
    users_api.update_last_connection_date(user)
    tokens = create_user_jwt_tokens(
        user=user,
        device_info=device_info,
    )
    return tokens.access, tokens.refresh


def _block_user_connection(user_id: int, duration: int) -> None:
    get_redis_client().set(USER_BAN_REDIS_KEY % user_id, 1, ex=duration)
    logger.info(
        "Failed authentication attempt",
        extra={"user": user_id, "avoid_current_user": True, "success": False},
        technical_message_id="users.login",
    )


def _is_user_blocked(user_id: int) -> bool:
    return get_redis_client().exists(USER_BAN_REDIS_KEY % user_id) == 1


@blueprint.native_route("/signin", version="v3", methods=["POST"])
@atomic()
@spectree_serialize(
    response_model=authentication.SigninResponseV3,
    on_success_status=200,
    on_error_statuses=[400, 401],
    api=blueprint.api,
)
def signin(body: authentication.SigninRequestV3) -> authentication.SigninResponseV3:
    if FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active():
        try:
            api_recaptcha.check_native_app_recaptcha_token(body.token)
        except (api_recaptcha.ReCaptchaException, api_recaptcha.InvalidRecaptchaTokenException):
            raise ApiErrors({"token": "Le token est invalide"}, 401)
    try:
        user = users_repo.get_user_with_credentials(body.identifier, body.password, allow_inactive=True)
    except users_exceptions.UnvalidatedAccount as exc:
        raise ApiErrors(
            {"code": "EMAIL_NOT_VALIDATED", "general": ["L'email n'a pas été validé."]}, status_code=401
        ) from exc
    except users_exceptions.CredentialsException as exc:
        raise ApiErrors({"general": ["Identifiant ou Mot de passe incorrect"]}, status_code=401) from exc

    if user.account_state.is_deleted or user.account_state == user_models.AccountState.ANONYMIZED:
        raise ApiErrors({"general": ["Identifiant ou Mot de passe incorrect"]}, status_code=401)

    if _is_user_blocked(user.id):
        raise ApiErrors({"general": ["Identifiant ou Mot de passe incorrect"]}, status_code=401)

    available_mfa = _get_available_mfa(user)
    session = MfaAuthSession(
        user_id=user.id,
        expiration=int(time.time()) + settings.NATIVE_APP_AUTHENTICATION_SESSION_MAX_DURATION,
        available_second_factor=available_mfa,
        current_step=None,
        device_info=body.device_info,
    )

    token = _save_auth_session(session)

    return authentication.SigninResponseV3(
        mfa_offers=[_get_mfa_offer(mfa, token) for mfa in available_mfa],
        expiration=session.expiration,
    )


@blueprint.native_route("/otp_mail/<token>", version="v3", methods=["GET"])
@atomic()
@spectree_serialize(
    response_model=authentication.OtpChallengeV3,
    on_success_status=200,
    on_error_statuses=[401],
    api=blueprint.api,
)
def otp_mail(token: str) -> authentication.OtpChallengeV3:
    session = _load_auth_session(token, SecondFactor.OTP_MAIL)

    if session.current_step and session.current_step["renewal_email"] > time.time():
        _block_user_connection(session.user_id, settings.NATIVE_APP_AUTHENTICATION_BAN_DURATION)
        raise ApiErrors({"general": ["Refresh trop rapide"]}, status_code=401)

    otp_characters: list[str] = []
    for i in range(settings.NATIVE_APP_AUTHENTICATION_OTP_LENGTH):
        otp_characters.append(secrets.choice(settings.NATIVE_APP_AUTHENTICATION_OTP_CHARACTERS))
    otp = "".join(otp_characters)

    # TODO: send otp

    if session.current_step and "retry_left" in session.current_step:
        retry_left = session.current_step["retry_left"]
    else:
        retry_left = settings.NATIVE_APP_AUTHENTICATION_OTP_RETRY

    session.current_step = {
        "otp": otp,
        "renewal_email": int(time.time()) + settings.NATIVE_APP_AUTHENTICATION_OTP_RENEWAL_EMAIL,
        "retry_left": retry_left,
    }

    token = _save_auth_session(session)

    return authentication.OtpChallengeV3(
        new_email_sent=True,
        expiration=session.expiration,
        renewal_email=session.current_step["renewal_email"],
        retry_left=session.current_step["retry_left"],
        char_count=len(otp),
        response_endpoint=url_for(".submit_otp_mail", token=token),
    )


@blueprint.native_route("/otp_mail/<token>", version="v3", methods=["POST"])
@atomic()
@spectree_serialize(
    response_model=authentication.OtpResponseV3,
    on_success_status=200,
    on_error_statuses=[401],
    api=blueprint.api,
)
def submit_otp_mail(body: authentication.OtpRequestV3, token: str) -> authentication.OtpResponseV3:
    session = _load_auth_session(token, SecondFactor.OTP_MAIL)

    if not session.current_step:
        _block_user_connection(session.user_id, settings.NATIVE_APP_AUTHENTICATION_BAN_DURATION)
        raise ApiErrors({"general": ["Workflow violation"]}, status_code=401)

    if body.response != session.current_step["otp"]:
        session.current_step["retry_left"] -= 1
        if session.current_step["retry_left"] <= 0:
            _block_user_connection(session.user_id, settings.NATIVE_APP_AUTHENTICATION_BAN_DURATION)
            raise ApiErrors({"ban_expiration": int(time.time()) + settings.NATIVE_APP_AUTHENTICATION_BAN_DURATION}, 401)
        token = _save_auth_session(session)
        return authentication.OtpResponseV3(
            expiration=session.expiration,
            renewal_email=session.current_step["renewal_email"],
            retry_left=session.current_step["retry_left"],
            char_count=len(session.current_step["otp"]),
            response_endpoint=url_for(".submit_otp_mail", token=token),
            session_tokens=None,
        )

    user = db.session.query(user_models.User).filter_by(id=session.user_id).one_or_none()
    if not user:
        # this should not be possible but let's be defensive
        raise ApiErrors({"general": ["L'utilisateur n'existe plus"]}, status_code=401)

    access, refresh = _conclude_authentication(user, session.device_info)

    return authentication.OtpResponseV3(
        expiration=0,
        renewal_email=0,
        retry_left=0,
        char_count=0,
        response_endpoint="",
        session_tokens=authentication.UserAuthenticatedV3(
            refresh_token=refresh,
            access_token=access,
            account_state=user.account_state,
        ),
    )
