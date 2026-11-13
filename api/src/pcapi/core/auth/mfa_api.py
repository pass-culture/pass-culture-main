import enum
import logging
import secrets
import time

import pydantic
from werkzeug.exceptions import NotFound

from pcapi import settings
from pcapi.core import token as token_utils
from pcapi.core.mails.transactional.users import multi_factor_authentication as mfa_mails
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.core.users.sessions import create_user_jwt_tokens
from pcapi.core.users.sessions import disconnect_native_user_sessions
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.native.v3.serialization import authentication
from pcapi.utils.redis import get_redis_client


logger = logging.getLogger(__name__)


USER_BAN_REDIS_KEY = "native:user:authentication_forbidden:%s"


class SecondFactor(enum.StrEnum):
    OTP_MAIL = "OTP_MAIL"


class AuthenticationViolation(Exception):
    """The user broke the authentication workflow and must be blocked, see `block_user_connection`"""

    def __init__(self, user_id: int, errors: dict) -> None:
        super().__init__()
        self.user_id = user_id
        self.errors = errors


class OtpMailStep(pydantic.BaseModel):
    otp: str
    next_email_at: int
    retry_left: int


class MfaAuthSession(pydantic.BaseModel):
    user_id: int
    expiration: int
    available_second_factors: list[SecondFactor]
    current_step: OtpMailStep | None
    device_info: authentication.DeviceInfoV3


def _get_available_mfas(user: users_models.User) -> list[SecondFactor]:
    return [SecondFactor.OTP_MAIL]


def _check_user_can_authenticate(user: users_models.User) -> None:
    if user.account_state.is_deleted or user.account_state == users_models.AccountState.ANONYMIZED:
        raise ApiErrors({"general": ["Identifiant ou Mot de passe incorrect"]})


def check_user_id_banned(user_id: int) -> None:
    ban_expiration = get_redis_client().ttl(USER_BAN_REDIS_KEY % user_id)
    if ban_expiration != -2:
        # a banned user cannot continue an authentication process
        raise ApiErrors(
            {
                "ban_expiration": max(int(time.time()) + ban_expiration, 0),
            },
            status_code=403,
        )


def block_user_connection(user_id: int) -> None:
    """
    Ban the user and delete all their native sessions.

    The caller must not raise after this call: an exception would make @atomic roll back the
    sessions disconnection.
    """
    get_redis_client().set(USER_BAN_REDIS_KEY % user_id, 1, ex=settings.NATIVE_APP_AUTHENTICATION_BAN_DURATION)
    disconnect_native_user_sessions(user_id=user_id)

    user = users_repository.find_user_by_id(user_id)
    if user:
        mfa_mails.send_failed_mfa_email(user)
    else:
        logger.error(
            "User disappeared during MFA",
            extra={"user_id": user_id, "avoid_current_user": True, "success": False},
            technical_message_id="users.login",
        )

    logger.info(
        "Failed authentication attempt",
        extra={"user_id": user_id, "avoid_current_user": True, "success": False},
        technical_message_id="users.login",
    )


def check_first_factor(identifier: str, password: str) -> users_models.User:
    try:
        user = users_repository.get_user_with_credentials(identifier, password, allow_inactive=True)
    except users_exceptions.UnvalidatedAccount as exc:
        raise ApiErrors({"code": "EMAIL_NOT_VALIDATED", "general": ["L'email n'a pas été validé."]}) from exc
    except users_exceptions.CredentialsException as exc:
        raise ApiErrors({"general": ["Identifiant ou Mot de passe incorrect"]}) from exc

    _check_user_can_authenticate(user)
    check_user_id_banned(user.id)

    return user


def save_auth_session(session: MfaAuthSession) -> str:
    if session.expiration < time.time():
        raise ApiErrors({"session": ["Session déjà expirée"]}, status_code=422)

    return token_utils.create_token(
        token_type=token_utils.TokenType.NATIVE_AUTH_SESSION,
        at=session.expiration,
        data=session.model_dump(mode="json"),
    )


def create_auth_session(
    user: users_models.User, device_info: authentication.DeviceInfoV3
) -> tuple[MfaAuthSession, str]:
    session = MfaAuthSession(
        user_id=user.id,
        expiration=int(time.time()) + settings.NATIVE_APP_AUTHENTICATION_SESSION_MAX_DURATION,
        available_second_factors=_get_available_mfas(user),
        current_step=None,
        device_info=device_info,
    )
    return session, save_auth_session(session)


def load_auth_session(token: str, second_factor: SecondFactor) -> MfaAuthSession:
    try:
        data = token_utils.load_token(token_type=token_utils.TokenType.NATIVE_AUTH_SESSION, token=token)
    except users_exceptions.InvalidToken as exc:
        raise ApiErrors({"token": ["Token invalide"]}, status_code=401) from exc

    if not data:
        raise ApiErrors({"token": ["Token invalide"]}, status_code=401)

    session = MfaAuthSession.model_validate(data)
    check_user_id_banned(session.user_id)

    # check if this factor is available for this session
    if second_factor not in session.available_second_factors:
        raise AuthenticationViolation(session.user_id, {"token": ["Méthode d'authentification invalide"]})
    # once a factor has been selected, it is the only one available
    session.available_second_factors = [second_factor]

    return session


def get_or_renew_otp_mail_step(session: MfaAuthSession) -> tuple[OtpMailStep, bool]:
    """Return the current step of the session, and whether a new email has been sent"""
    if session.current_step and session.current_step.next_email_at > time.time():
        return session.current_step, False

    otp_characters: list[str] = []
    for i in range(settings.NATIVE_APP_AUTHENTICATION_OTP_LENGTH):
        otp_characters.append(secrets.choice(settings.NATIVE_APP_AUTHENTICATION_OTP_CHARACTERS))
    otp = "".join(otp_characters)

    user = users_repository.find_user_by_id(session.user_id)
    if not user:
        raise NotFound()

    mfa_mails.send_otp_by_email(user, otp)

    if session.current_step:
        retry_left = session.current_step.retry_left
    else:
        retry_left = settings.NATIVE_APP_AUTHENTICATION_OTP_RETRY

    session.current_step = OtpMailStep(
        otp=otp,
        next_email_at=int(time.time()) + settings.NATIVE_APP_AUTHENTICATION_OTP_RENEWAL_EMAIL,
        retry_left=retry_left,
    )
    return session.current_step, True


def get_otp_mail_step(session: MfaAuthSession) -> OtpMailStep:
    if not session.current_step:
        raise AuthenticationViolation(session.user_id, {"general": ["Workflow violation"]})
    return session.current_step


def check_otp_mail_response(user_id: int, step: OtpMailStep, response: str) -> bool:
    """Return whether the response is valid. A wrong response consumes one retry of `step`"""
    if response == step.otp:
        return True

    step.retry_left -= 1
    if step.retry_left <= 0:
        raise AuthenticationViolation(
            user_id, {"ban_expiration": int(time.time()) + settings.NATIVE_APP_AUTHENTICATION_BAN_DURATION}
        )
    return False


def get_session_user(session: MfaAuthSession) -> users_models.User:
    user = db.session.query(users_models.User).filter_by(id=session.user_id).one_or_none()
    if not user:
        # this should not be possible but let's be defensive
        raise ApiErrors({"general": ["L'utilisateur n'existe plus"]}, status_code=403)

    _check_user_can_authenticate(user)
    return user


def conclude_authentication(user: users_models.User, device_info: authentication.DeviceInfoV3) -> tuple[str, str]:
    logger.info(
        "Successful authentication attempt",
        extra={
            "identifier": user.email,
            "user": user.id,
            "avoid_current_user": True,
            "success": True,
            "api_version": "v3",
            "feature": "users",
            "action": "login",
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
