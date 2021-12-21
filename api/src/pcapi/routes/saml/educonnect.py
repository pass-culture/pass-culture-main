import datetime
import logging
from typing import Optional
from urllib.parse import urlencode

from flask import current_app as app
from flask import redirect
from flask import request
from werkzeug.wrappers import Response

from pcapi import settings
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import exceptions as fraud_exceptions
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.core.users.constants import ELIGIBILITY_AGE_18
from pcapi.core.users.external.educonnect import api as educonnect_api
from pcapi.core.users.external.educonnect import exceptions as educonnect_exceptions
from pcapi.routes.native.security import authenticated_user_required

from . import blueprint


logger = logging.getLogger(__name__)

ERROR_PAGE_URL = f"{settings.WEBAPP_V2_URL}/idcheck/educonnect/erreur?"


@blueprint.saml_blueprint.route("educonnect/login", methods=["GET"])
@authenticated_user_required
def login_educonnect(user: users_models.User) -> Response:
    should_redirect = request.args.get("redirect", default=True, type=lambda v: v.lower() == "true")
    redirect_url = educonnect_api.get_login_redirect_url(user)
    response = Response()

    if not should_redirect:
        response.status_code = 204
        response.headers["educonnect-redirect"] = redirect_url
        response.headers["Access-Control-Expose-Headers"] = "educonnect-redirect"
    else:
        response = redirect(redirect_url, code=302)

    response.headers["Cache-Control"] = "no-cache, no-store"
    response.headers["Pragma"] = "no-cache"

    return response


@blueprint.saml_blueprint.route("acs", methods=["POST"])
def on_educonnect_authentication_response() -> Response:  # pylint: disable=too-many-return-statements
    try:
        educonnect_user = educonnect_api.get_educonnect_user(request.form["SAMLResponse"])

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

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error after educonnect authentication: %s", exc)
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
            "date_of_birth": educonnect_user.birth_date.isoformat(),
            "educonnect_connection_date": educonnect_user.connection_datetime.isoformat(),
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

    educonnect_content = fraud_models.EduconnectContent(
        birth_date=educonnect_user.birth_date,
        educonnect_id=educonnect_user.educonnect_id,
        first_name=educonnect_user.first_name,
        ine_hash=educonnect_user.ine_hash,
        last_name=educonnect_user.last_name,
        registration_datetime=datetime.datetime.now(),
        school_uai=educonnect_user.school_uai,
        student_level=educonnect_user.student_level,
    )

    try:
        fraud_api.on_educonnect_result(user, educonnect_content)
    except fraud_exceptions.BeneficiaryFraudResultCannotBeDowngraded:
        logger.exception("Trying to downgrade FraudResult after eduonnect response", extra={"user_id": user.id})
        return redirect(ERROR_PAGE_URL + urlencode(base_query_param), code=302)
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("Error on educonnect result: %s", e, extra={"user_id": user.id})
        return redirect(ERROR_PAGE_URL + urlencode(base_query_param), code=302)

    try:
        # TODO(viconnex): use generic subscription_api.on_successful_application
        subscription_api.create_beneficiary_import_after_educonnect(
            user, fraud_api.get_eligibility_type(educonnect_content)
        )
    except fraud_exceptions.UserAgeNotValid:
        logger.warning(
            "User age not valid",
            extra={"userId": user.id, "educonnectId": educonnect_user.educonnect_id, "age": user.age},
        )
        error_query_param = {
            "code": "UserAgeNotValid18YearsOld"
            if users_utils.get_age_from_birth_date(educonnect_content.birth_date) == ELIGIBILITY_AGE_18
            else "UserAgeNotValid"
        } | base_query_param
        return redirect(ERROR_PAGE_URL + urlencode(error_query_param), code=302)

    except fraud_exceptions.NotWhitelistedINE:
        error_query_param = {"code": "UserNotWhitelisted"} | base_query_param
        return redirect(ERROR_PAGE_URL + urlencode(error_query_param), code=302)

    except fraud_exceptions.UserAlreadyBeneficiary:
        logger.warning(
            "User already beneficiary",
            extra={"userId": user.id, "educonnectId": educonnect_user.educonnect_id},
        )
        error_query_param = {"code": "UserAlreadyBeneficiary"} | base_query_param
        return redirect(ERROR_PAGE_URL + urlencode(error_query_param), code=302)

    except fraud_exceptions.FraudException as e:
        logger.warning(
            "Fraud suspicion after Educonnect authentication: %s",
            e,
            extra={"userId": user.id, "educonnectId": educonnect_user.educonnect_id},
        )

    except Exception as e:  # pylint: disable=broad-except
        logger.exception("Error while creating BeneficiaryImport from Educonnect: %s", e, extra={"user_id": user.id})
        return redirect(ERROR_PAGE_URL, code=302)

    user_information_validation_base_url = f"{settings.WEBAPP_V2_URL}/validation?"
    query_params = {
        "firstName": educonnect_user.first_name,
        "lastName": educonnect_user.last_name,
        "dateOfBirth": educonnect_user.birth_date,
    } | base_query_param

    return redirect(user_information_validation_base_url + urlencode(query_params), code=302)


def _user_id_from_saml_request_id(saml_request_id: str) -> Optional[int]:
    key = educonnect_api.build_saml_request_id_key(saml_request_id)
    return app.redis_client.get(key)
