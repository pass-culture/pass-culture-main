import logging
from urllib.parse import urlencode

from flask import current_app as app
from flask import redirect
from flask import request
from werkzeug.wrappers import Response

from pcapi import settings
from pcapi.connectors.beneficiaries.educonnect import educonnect_connector
from pcapi.connectors.beneficiaries.educonnect import exceptions as educonnect_exceptions
from pcapi.connectors.beneficiaries.educonnect import models as educonnect_models
from pcapi.core import logging as core_logging
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription.educonnect import api as educonnect_subscription_api
from pcapi.core.subscription.educonnect import exceptions as educonnect_subscription_exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.core.users.constants import ELIGIBILITY_AGE_18
from pcapi.routes.native.security import authenticated_and_active_user_required

from . import blueprint


logger = logging.getLogger(__name__)

ERROR_PAGE_URL = f"{settings.WEBAPP_V2_URL}/educonnect/erreur?"
SUCCESS_PAGE_URL = f"{settings.WEBAPP_V2_URL}/educonnect/validation?"


def _log_for_educonnect_supervision(log_message: str, user_id: int) -> None:
    core_logging.log_for_supervision(
        logger=logging.getLogger(__name__),
        log_level=logging.INFO,
        log_message=f"[EDUCONNECT AUTHENTICATION] {log_message}",
        extra={"user_id": user_id},
    )


@blueprint.saml_blueprint.route("educonnect/login", methods=["GET"])
@authenticated_and_active_user_required
def login_educonnect(user: users_models.User) -> Response:
    should_redirect = request.args.get("redirect", default=True, type=lambda v: v.lower() == "true")
    redirect_url = educonnect_connector.get_login_redirect_url(user)
    response = Response()

    if not should_redirect:
        response.status_code = 204
        response.headers["educonnect-redirect"] = redirect_url
        response.headers["Access-Control-Expose-Headers"] = "educonnect-redirect"
        _log_for_educonnect_supervision("Sending redirect url (webapp)", user.id)  # type: ignore [arg-type]
    else:
        response = redirect(redirect_url, code=302)
        _log_for_educonnect_supervision("Redirecting to educonnect (app)", user.id)  # type: ignore [arg-type]

    response.headers["Cache-Control"] = "no-cache, no-store"
    response.headers["Pragma"] = "no-cache"

    return response


@blueprint.saml_blueprint.route("acs", methods=["POST"])
def on_educonnect_authentication_response() -> Response:
    try:
        educonnect_user = educonnect_connector.get_educonnect_user(request.form["SAMLResponse"])

    except educonnect_exceptions.ResponseTooOld:
        logger.warning("Educonnect saml_response too old")
        return redirect(ERROR_PAGE_URL, code=302)

    except educonnect_exceptions.UserTypeNotStudent as exc:
        logger.info(
            "Wrong user type of educonnect user",
            extra={"user_id": _user_id_from_saml_request_id(exc.request_id), "saml_request_id": exc.request_id},
        )
        error_query_param = {"code": "UserTypeNotStudent", "logoutUrl": exc.logout_url}
        return redirect(ERROR_PAGE_URL + urlencode(error_query_param), code=302)

    except educonnect_exceptions.ParsingError as exc:
        logger.exception("KeyError after educonnect exception", extra={"parsed_data": exc.parsed_dict})
        return redirect(ERROR_PAGE_URL + urlencode({"logout_url": exc.logout_url}), code=302)

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error after educonnect authentication")
        return redirect(ERROR_PAGE_URL, code=302)

    user_id = _user_id_from_saml_request_id(educonnect_user.saml_request_id)
    base_query_param = {"logoutUrl": educonnect_user.logout_url}

    if user_id is None:
        logger.error(
            "No user_id corresponding to educonnect request_id", extra={"request_id": educonnect_user.saml_request_id}
        )
        return redirect(ERROR_PAGE_URL + urlencode(base_query_param), code=302)

    user = users_models.User.query.get(user_id)

    logger.info(
        "Received educonnect authentication response",
        extra={
            "user_email": user.email,
            "user_id": user.id,
            "date_of_birth": educonnect_user.birth_date.isoformat(),
            "educonnect_connection_date": educonnect_user.connection_datetime.isoformat()
            if educonnect_user.connection_datetime
            else None,
            "educonnect_id": educonnect_user.educonnect_id,
            "ine_hash": educonnect_user.ine_hash,
            "first_name": educonnect_user.first_name,
            "last_name": educonnect_user.last_name,
            "logout_url": educonnect_user.logout_url,
            "user_type": educonnect_user.user_type,
            "saml_request_id": educonnect_user.saml_request_id,
            "school_uai": educonnect_user.school_uai,
            "student_level": educonnect_user.student_level,
        },
    )

    try:
        error_codes = educonnect_subscription_api.handle_educonnect_authentication(user, educonnect_user)
    except educonnect_subscription_exceptions.EduconnectSubscriptionException:
        return redirect(ERROR_PAGE_URL + urlencode(base_query_param), code=302)

    if error_codes:
        return _on_educonnect_authentication_errors(error_codes, educonnect_user, base_query_param)

    success_query_params = {
        "firstName": educonnect_user.first_name,
        "lastName": educonnect_user.last_name,
        "dateOfBirth": educonnect_user.birth_date,
    } | base_query_param

    return redirect(SUCCESS_PAGE_URL + urlencode(success_query_params), code=302)


def _user_id_from_saml_request_id(saml_request_id: str) -> int | None:
    key = educonnect_connector.build_saml_request_id_key(saml_request_id)
    return app.redis_client.get(key)  # type: ignore [attr-defined]


def _on_educonnect_authentication_errors(
    error_codes: list[fraud_models.FraudReasonCode],
    educonnect_user: educonnect_models.EduconnectUser,
    base_query_param: dict,
) -> Response:
    error_query_param = base_query_param

    if fraud_models.FraudReasonCode.DUPLICATE_USER in error_codes:
        error_query_param |= {"code": "DuplicateUser"}
    elif fraud_models.FraudReasonCode.DUPLICATE_INE in error_codes:
        error_query_param |= {"code": "DuplicateINE"}
    elif fraud_models.FraudReasonCode.AGE_NOT_VALID or fraud_models.FraudReasonCode.NOT_ELIGIBLE in error_codes:
        if users_utils.get_age_from_birth_date(educonnect_user.birth_date) == ELIGIBILITY_AGE_18:
            error_query_param |= {"code": "UserAgeNotValid18YearsOld"}
        else:
            error_query_param |= {"code": "UserAgeNotValid"}

    return redirect(ERROR_PAGE_URL + urlencode(error_query_param), code=302)
