import logging
from os import path

from flask import redirect
from flask import request
from saml2 import BINDING_HTTP_POST
from saml2 import xmldsig
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config
from saml2.validate import ResponseLifetimeExceed

from pcapi import settings
from pcapi.models.api_errors import ApiErrors

from . import blueprint


logger = logging.getLogger(__name__)

BASEDIR = path.dirname(path.abspath(__file__))
FILES_DIR = "files"
PRIVATE_KEY_FILE_PATH = path.join(BASEDIR, f"{FILES_DIR}/private.key")
PUBLIC_CERTIFICATE_FILE_PATH = path.join(BASEDIR, f"{FILES_DIR}/public.cert")

with open(PUBLIC_CERTIFICATE_FILE_PATH, "w") as certificate_file:
    certificate_file.write(settings.EDUCONNECT_SP_CERTIFICATE)
with open(PRIVATE_KEY_FILE_PATH, "w") as key_file:
    key_file.write(settings.EDUCONNECT_SP_PRIVATE_KEY)


def get_educonnect_saml_client():
    entityid = f"{settings.API_URL_FOR_EDUCONNECT}/saml/metadata.xml"
    https_acs_url = f"{settings.API_URL_FOR_EDUCONNECT}/saml/acs/"

    config = {
        "entityid": entityid,
        "metadata": {
            "local": [path.join(BASEDIR, f"{FILES_DIR}/educonnect.metadata.xml")],
        },
        "service": {
            "sp": {
                "endpoints": {
                    "assertion_consumer_service": [(https_acs_url, BINDING_HTTP_POST)],
                },
                "allow_unsolicited": True,
                "authn_requests_signed": True,
                "logout_requests_signed": True,
                "want_assertions_signed": True,
                "want_response_signed": True,
            }
        },
        "signing_algorithm": xmldsig.SIG_RSA_SHA256,
        "digest_algorithm": xmldsig.DIGEST_SHA256,
        "cert_file": PUBLIC_CERTIFICATE_FILE_PATH,
        "key_file": PRIVATE_KEY_FILE_PATH,
        "encryption_keypairs": [
            {"key_file": PRIVATE_KEY_FILE_PATH, "cert_file": PUBLIC_CERTIFICATE_FILE_PATH}  # private part
        ],
    }

    saml2_config = Saml2Config()
    saml2_config.load(config)
    saml2_config.allow_unknown_attributes = True

    saml2_client = Saml2Client(config=saml2_config)

    return saml2_client


@blueprint.saml_blueprint.route("educonnect/login", methods=["GET"])
# TODO (viconnex): add @authenticated_user_required decorator
def login_educonnect() -> None:
    saml_client = get_educonnect_saml_client()
    request_id, info = saml_client.prepare_for_authenticate()

    redirect_url = next(header[1] for header in info["headers"] if header[0] == "Location")

    response = redirect(redirect_url, code=302)

    response.headers["Cache-Control"] = "no-cache, no-store"
    response.headers["Pragma"] = "no-cache"

    logger.info("Sending saml login request with educonnect request_id = %s", request_id)

    return response


@blueprint.saml_blueprint.route("acs", methods=["POST"])
def on_educonnect_authentication_response() -> None:
    saml_client = get_educonnect_saml_client()
    try:
        authn_response = saml_client.parse_authn_request_response(request.form["SAMLResponse"], BINDING_HTTP_POST)
    except ResponseLifetimeExceed as exception:
        logger.error("Educonnect response more than 10 minutes old: %s", exception)
        raise ApiErrors({"saml_response": "Too old"})  # TODO: redirect user to error page
    except Exception as exception:
        logger.error("Impossible to parse educonnect saml response: %s", exception)
        raise ApiErrors()  # TODO: redirect user to error page

    educonnect_identity = authn_response.get_identity()

    saml_request_id = authn_response.in_response_to
    last_name = educonnect_identity.get("sn", [None])[0]
    first_name = educonnect_identity.get("givenName", [None])[0]
    educonnect_id = educonnect_identity.get(_get_field_oid("57"), [None])[0]
    date_of_birth = educonnect_identity.get(_get_field_oid("67"), [None])[0]
    educonnect_connection_date = educonnect_identity.get(_get_field_oid("6"), [None])[0]
    student_level = educonnect_identity.get(_get_field_oid("73"), [None])[0]

    logger.info(
        "Received educonnect authentication response",
        extra={
            "date_of_birth": date_of_birth,
            "educonnect_connection_date": educonnect_connection_date,
            "educonnect_id": educonnect_id,
            "first_name": first_name,
            "last_name": last_name,
            "saml_request_id": saml_request_id,
            "student_level": student_level,
        },
    )

    # TODO: redirect user to the right page
    return redirect(settings.WEBAPP_V2_URL, code=302)


def _get_field_oid(oid_key: str) -> str:
    return f"urn:oid:1.3.6.1.4.1.20326.10.999.1.{oid_key}"
