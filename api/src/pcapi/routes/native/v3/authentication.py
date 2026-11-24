import flask
from flask import url_for
from werkzeug.exceptions import NotFound

from pcapi.connectors import api_recaptcha
from pcapi.core.auth import mfa_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.routes.error_handlers.utils import generate_error_response
from pcapi.routes.native.v3.serialization import authentication
from pcapi.serialization.decorator import make_json_response
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from .. import blueprint


def _get_available_mfa(factor: mfa_api.SecondFactor, token: str) -> authentication.AvailableMfaV3:
    match factor:
        case mfa_api.SecondFactor.OTP_MAIL:
            return authentication.AvailableMfaV3(type=factor.value, endpoint=url_for(".otp_challenge"), mfa_token=token)
    raise ValueError(f"unknown second factor {factor}")


def _get_violation_errors(exc: mfa_api.MultifactorAuthenticationViolation) -> dict:
    match exc:
        case mfa_api.MultifactorAuthenticationInvalidSecondFactor():
            return {"token": ["Méthode d'authentification invalide"]}
        case mfa_api.MultifactorAuthenticationWorkflowViolation():
            return {"general": ["Workflow violation"]}
        case mfa_api.MultifactorAuthenticationTooManyAttempts():
            return {"banExpiration": exc.ban_expiration}
    raise ValueError(f"unknown authentication violation {type(exc)}")


def _block_user_connection(exc: mfa_api.MultifactorAuthenticationViolation) -> flask.Response:
    """
    Block the user and return the error response.

    The response must be returned by the route instead of raising an `ApiErrors`: an exception
    would make `atomic` roll back the sessions disconnection.
    """
    mfa_api.block_user_connection(exc.user_id)

    errors = _get_violation_errors(exc)
    response = generate_error_response(errors)
    response.status_code = 403
    return response


@blueprint.native_route("/signin", version="v3", methods=["POST"])
@atomic()
@spectree_serialize(
    response_model=authentication.SigninResponseV3,
    on_success_status=200,
    on_error_statuses=[400, 401, 403],
    api=blueprint.api,
)
def signin(body: authentication.SigninRequestV3) -> authentication.SigninResponseV3:
    if FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active():
        try:
            api_recaptcha.check_native_app_recaptcha_token(body.captcha_token)
        except (api_recaptcha.ReCaptchaException, api_recaptcha.InvalidRecaptchaTokenException):
            raise ApiErrors({"token": "Le token est invalide"}, 401)

    try:
        user = mfa_api.check_first_factor(body.identifier, body.password)
    except users_exceptions.UnvalidatedAccount as exc:
        raise ApiErrors({"code": "EMAIL_NOT_VALIDATED", "general": ["L'email n'a pas été validé."]}) from exc
    except users_exceptions.CredentialsException as exc:
        raise ApiErrors({"general": ["Identifiant ou Mot de passe incorrect"]}) from exc
    except mfa_api.MultifactorAuthenticationBanned as exc:
        raise ApiErrors({"banExpiration": exc.ban_expiration}, status_code=403) from exc

    session, token = mfa_api.create_auth_session(user, body.device_info)

    return authentication.SigninResponseV3(
        available_mfas=[_get_available_mfa(mfa, token) for mfa in session.available_second_factors],
        expiration=session.expiration,
    )


@blueprint.native_route("/otp/challenge", version="v3", methods=["POST"])
@atomic()
@spectree_serialize(
    response_model=authentication.OtpChallengeResponseV3,
    on_success_status=200,
    on_error_statuses=[401, 403, 422],
    api=blueprint.api,
    raw_response=True,
)
def otp_challenge(body: authentication.OtpChallengeRequestV3) -> flask.Response:
    try:
        session = mfa_api.load_auth_session(body.mfa_token, mfa_api.SecondFactor.OTP_MAIL)
    except users_exceptions.InvalidToken as exc:
        raise ApiErrors({"token": ["Token invalide"]}, status_code=401) from exc
    except mfa_api.MultifactorAuthenticationBanned as exc:
        raise ApiErrors({"banExpiration": exc.ban_expiration}, status_code=403) from exc
    except mfa_api.MultifactorAuthenticationViolation as exc:
        return _block_user_connection(exc)

    try:
        step, new_email_sent = mfa_api.get_or_renew_otp_mail_step(session)
    except users_exceptions.UserDoesNotExist as exc:
        raise NotFound() from exc
    try:
        token = mfa_api.save_auth_session(session)
    except mfa_api.MultifactorAuthenticationExpiredSession as exc:
        raise ApiErrors({"session": ["Session déjà expirée"]}, status_code=422) from exc

    return make_json_response(
        authentication.OtpChallengeResponseV3(
            new_email_sent=new_email_sent,
            expiration=session.expiration,
            next_email_at=step.next_email_at,
            retry_left=step.retry_left,
            char_count=len(step.otp),
            response_endpoint=url_for(".submit_otp_response"),
            mfa_token=token,
        ),
        status_code=200,
        by_alias=True,
    )


@blueprint.native_route("/otp/response", version="v3", methods=["POST"])
@atomic()
@spectree_serialize(
    response_model=authentication.OtpResponseV3,
    on_success_status=200,
    on_error_statuses=[400, 401, 403, 422],
    api=blueprint.api,
    raw_response=True,
)
def submit_otp_response(body: authentication.OtpRequestV3) -> flask.Response:
    try:
        session = mfa_api.load_auth_session(body.mfa_token, mfa_api.SecondFactor.OTP_MAIL)
        step = mfa_api.get_otp_mail_step(session)
        is_valid_response = mfa_api.check_otp_mail_response(session.user_id, step, body.response)
    except users_exceptions.InvalidToken as exc:
        raise ApiErrors({"token": ["Token invalide"]}, status_code=401) from exc
    except mfa_api.MultifactorAuthenticationBanned as exc:
        raise ApiErrors({"banExpiration": exc.ban_expiration}, status_code=403) from exc
    except mfa_api.MultifactorAuthenticationViolation as exc:
        return _block_user_connection(exc)

    if not is_valid_response:
        try:
            token = mfa_api.save_auth_session(session)
        except mfa_api.MultifactorAuthenticationExpiredSession as exc:
            raise ApiErrors({"session": ["Session déjà expirée"]}, status_code=422) from exc
        return make_json_response(
            authentication.OtpResponseV3(
                expiration=session.expiration,
                next_email_at=step.next_email_at,
                retry_left=step.retry_left,
                char_count=len(step.otp),
                response_endpoint=url_for(".submit_otp_response"),
                mfa_token=token,
                session_tokens=None,
            ),
            status_code=200,
            by_alias=True,
        )

    try:
        user = mfa_api.get_session_user(session)
    except (users_exceptions.InvalidIdentifier, users_exceptions.UserDoesNotExist) as exc:
        raise ApiErrors({"general": ["Identifiant ou Mot de passe incorrect"]}) from exc

    access, refresh = mfa_api.conclude_authentication(user, session.device_info)

    return make_json_response(
        authentication.OtpResponseV3(
            expiration=0,
            next_email_at=0,
            retry_left=0,
            char_count=0,
            response_endpoint="",
            session_tokens=authentication.UserAuthenticatedV3(
                refresh_token=refresh,
                access_token=access,
                account_state=user.account_state,
            ),
            mfa_token=None,
        ),
        status_code=200,
        by_alias=True,
    )
