import flask
from flask import url_for

from pcapi.connectors import api_recaptcha
from pcapi.core.auth import mfa_api
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.routes.error_handlers.utils import generate_error_response
from pcapi.routes.native.v3.serialization import authentication
from pcapi.routes.serialization import HttpBodyModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from .. import blueprint


def _get_mfa_offer(factor: mfa_api.SecondFactor, token: str) -> authentication.MfaOfferV3:
    match factor:
        case mfa_api.SecondFactor.OTP_MAIL:
            return authentication.MfaOfferV3(
                type=factor.value,
                endpoint=url_for(".otp_mail", token=token),
            )
    raise ValueError(f"unknown second factor {factor}")


def _json_response(content: HttpBodyModel) -> flask.Response:
    response = flask.make_response(content.model_dump_json(by_alias=True), 200)
    response.mimetype = "application/json"
    return response


def _block_user_connection(exc: mfa_api.AuthenticationViolation) -> flask.Response:
    """
    Block the user and return the error response.

    The response must be returned by the route instead of raising an `ApiErrors`: an exception
    would make `atomic` roll back the sessions disconnection.
    """
    mfa_api.block_user_connection(exc.user_id)

    response = generate_error_response(exc.errors)
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
            api_recaptcha.check_native_app_recaptcha_token(body.token)
        except (api_recaptcha.ReCaptchaException, api_recaptcha.InvalidRecaptchaTokenException):
            raise ApiErrors({"token": "Le token est invalide"}, 401)

    user = mfa_api.check_first_factor(body.identifier, body.password)
    session, token = mfa_api.create_auth_session(user, body.device_info)

    return authentication.SigninResponseV3(
        mfa_offers=[_get_mfa_offer(mfa, token) for mfa in session.available_second_factors],
        expiration=session.expiration,
    )


@blueprint.native_route("/otp_mail/<token>", version="v3", methods=["GET"])
@atomic()
@spectree_serialize(
    response_model=authentication.OtpChallengeV3,
    on_success_status=200,
    on_error_statuses=[403],
    api=blueprint.api,
    raw_response=True,
)
def otp_mail(token: str) -> flask.Response:
    try:
        session = mfa_api.load_auth_session(token, mfa_api.SecondFactor.OTP_MAIL)
    except mfa_api.AuthenticationViolation as exc:
        return _block_user_connection(exc)

    step, new_email_sent = mfa_api.get_or_renew_otp_mail_step(session)
    token = mfa_api.save_auth_session(session)

    return _json_response(
        authentication.OtpChallengeV3(
            new_email_sent=new_email_sent,
            expiration=session.expiration,
            next_email_at=step.next_email_at,
            retry_left=step.retry_left,
            char_count=len(step.otp),
            response_endpoint=url_for(".submit_otp_mail", token=token),
        )
    )


@blueprint.native_route("/otp_mail/<token>", version="v3", methods=["POST"])
@atomic()
@spectree_serialize(
    response_model=authentication.OtpResponseV3,
    on_success_status=200,
    on_error_statuses=[401],
    api=blueprint.api,
    raw_response=True,
)
def submit_otp_mail(body: authentication.OtpRequestV3, token: str) -> flask.Response:
    try:
        session = mfa_api.load_auth_session(token, mfa_api.SecondFactor.OTP_MAIL)
        step = mfa_api.get_otp_mail_step(session)
        is_valid_response = mfa_api.check_otp_mail_response(session.user_id, step, body.response)
    except mfa_api.AuthenticationViolation as exc:
        return _block_user_connection(exc)

    if not is_valid_response:
        token = mfa_api.save_auth_session(session)
        return _json_response(
            authentication.OtpResponseV3(
                expiration=session.expiration,
                next_email_at=step.next_email_at,
                retry_left=step.retry_left,
                char_count=len(step.otp),
                response_endpoint=url_for(".submit_otp_mail", token=token),
                session_tokens=None,
            )
        )

    user = mfa_api.get_session_user(session)
    access, refresh = mfa_api.conclude_authentication(user, session.device_info)

    return _json_response(
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
        )
    )
