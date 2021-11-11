from datetime import datetime
import logging
from os import path

from flask import current_app as app
from saml2 import BINDING_HTTP_POST
from saml2 import xmldsig
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config
from saml2.validate import ResponseLifetimeExceed

from pcapi import settings
from pcapi.core.users import constants
from pcapi.core.users import models as user_models

from . import exceptions
from . import models


logger = logging.getLogger(__name__)

BASEDIR = path.dirname(path.abspath(__file__))
FILES_DIR = "files"
PRIVATE_KEY_FILE_PATH = path.join(BASEDIR, f"{FILES_DIR}/private.key")
PUBLIC_CERTIFICATE_FILE_PATH = path.join(BASEDIR, f"{FILES_DIR}/public.cert")

with open(PUBLIC_CERTIFICATE_FILE_PATH, "w") as certificate_file:
    certificate_file.write(settings.EDUCONNECT_SP_CERTIFICATE)
with open(PRIVATE_KEY_FILE_PATH, "w") as key_file:
    key_file.write(settings.EDUCONNECT_SP_PRIVATE_KEY)


def get_saml_client() -> Saml2Client:
    entityid = f"{settings.API_URL_FOR_EDUCONNECT}/saml/metadata.xml"
    https_acs_url = f"{settings.API_URL_FOR_EDUCONNECT}/saml/acs/"

    config = {
        "entityid": entityid,
        "metadata": {
            "local": [
                path.join(BASEDIR, f"{FILES_DIR}/educonnect.{'production' if settings.IS_PROD else 'pr4'}.metadata.xml")
            ],
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


def get_login_redirect_url(user: user_models.User) -> str:
    saml_client = get_saml_client()
    saml_request_id, info = saml_client.prepare_for_authenticate()

    logger.info(
        "Sending saml login request with educonnect request_id = %s", saml_request_id, extra={"user_id": user.id}
    )
    key = build_saml_request_id_key(saml_request_id)
    app.redis_client.set(name=key, value=user.id, ex=constants.EDUCONNECT_SAML_REQUEST_ID_TTL)

    redirect_url = next(header[1] for header in info["headers"] if header[0] == "Location")
    return redirect_url


def get_educonnect_user(saml_response: str) -> models.EduconnectUser:
    saml_client = get_saml_client()
    try:
        authn_response = saml_client.parse_authn_request_response(saml_response, BINDING_HTTP_POST)
    except ResponseLifetimeExceed as exception:
        logger.error("Educonnect response more than 10 minutes old: %s", exception)
        raise exceptions.ResponseTooOld()
    except Exception as exception:
        logger.error("Impossible to parse educonnect saml response: %s", exception)
        raise exceptions.EduconnectAuthenticationException()

    educonnect_identity = authn_response.get_identity()

    saml_request_id = authn_response.in_response_to

    try:
        return models.EduconnectUser(
            connection_datetime=datetime.strptime(educonnect_identity[_get_field_oid("6")][0], "%Y-%m-%d %H:%M:%S.%f"),
            birth_date=datetime.strptime(educonnect_identity[_get_field_oid("67")][0], "%Y-%m-%d").date(),
            educonnect_id=educonnect_identity[_get_field_oid("57")][0],
            first_name=educonnect_identity["givenName"][0],
            ine_hash=educonnect_identity[_get_field_oid("64")][0],
            last_name=educonnect_identity["sn"][0],
            logout_url=educonnect_identity[_get_field_oid("5")][0],
            saml_request_id=saml_request_id,
            student_level=educonnect_identity.get(_get_field_oid("73"), [None])[0],
        )
    except KeyError as exception:
        logger.error(
            "Key error raised when parsing educonnect saml response: %s",
            repr(exception),
            extra={"saml_request_id": saml_request_id},
        )
        raise exceptions.ParsingError()
    except Exception as exception:
        logger.error(
            "Error when parsing educonnect saml response: %s",
            repr(exception),
            extra={"saml_request_id": saml_request_id},
        )
        raise exceptions.ParsingError()


def _get_field_oid(oid_key: str) -> str:
    return f"urn:oid:1.3.6.1.4.1.20326.10.999.1.{oid_key}"


def build_saml_request_id_key(saml_request_id: str) -> str:
    return f"educonnect-saml-request-{saml_request_id}"
