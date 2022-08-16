from datetime import datetime
import logging
from os import path
import random
import string

from flask import current_app as app
from saml2 import BINDING_HTTP_POST
from saml2 import xmldsig
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config
from saml2.validate import ResponseLifetimeExceed

from pcapi import settings
from pcapi.core.users import constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models

from . import exceptions
from . import models


logger = logging.getLogger(__name__)

BASEDIR = path.dirname(path.abspath(__file__))
FILES_DIR = "files"

PRIVATE_KEY_FILE_PATH = path.join(BASEDIR, f"{FILES_DIR}/private.key")
PUBLIC_CERTIFICATE_FILE_PATH = path.join(BASEDIR, f"{FILES_DIR}/public.cert")

with open(PUBLIC_CERTIFICATE_FILE_PATH, "w", encoding="ascii") as certificate_file:
    certificate_file.write(settings.EDUCONNECT_SP_CERTIFICATE)
with open(PRIVATE_KEY_FILE_PATH, "w", encoding="ascii") as key_file:
    key_file.write(settings.EDUCONNECT_SP_PRIVATE_KEY)

PASS_CULTURE_IDENTITY_ID = f"{settings.API_URL_FOR_EDUCONNECT}/saml/metadata.xml"
PASS_CULTURE_ACS_URL = f"{settings.API_URL_FOR_EDUCONNECT}/saml/acs/"


def get_saml_client() -> Saml2Client:
    config = {
        "entityid": PASS_CULTURE_IDENTITY_ID,
        "metadata": {
            "local": [
                path.join(
                    BASEDIR,
                    f"{FILES_DIR}/educonnect-metadata/educonnect.{'production' if settings.IS_PROD else 'pr4'}.metadata.xml",
                )
            ],
        },
        "service": {
            "sp": {
                "endpoints": {
                    "assertion_consumer_service": [(PASS_CULTURE_ACS_URL, BINDING_HTTP_POST)],
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


def get_login_redirect_url(user: users_models.User) -> str:
    saml_client = get_saml_client()
    saml_request_id, info = saml_client.prepare_for_authenticate()

    logger.info(
        "Sending saml login request with educonnect request_id = %s", saml_request_id, extra={"user_id": user.id}
    )
    key = build_saml_request_id_key(saml_request_id)
    app.redis_client.set(name=key, value=user.id, ex=constants.EDUCONNECT_SAML_REQUEST_ID_TTL)  # type: ignore [attr-defined]

    redirect_url = next(header[1] for header in info["headers"] if header[0] == "Location")
    return redirect_url


def get_educonnect_user(saml_response: str) -> models.EduconnectUser:
    if settings.IS_PERFORMANCE_TESTS:
        return _get_mocked_user_for_performance_tests(saml_response)
    saml_client = get_saml_client()
    try:
        authn_response = saml_client.parse_authn_request_response(saml_response, BINDING_HTTP_POST)
    except ResponseLifetimeExceed:
        logger.exception("Educonnect response more than 10 minutes old")
        raise exceptions.ResponseTooOld()
    except Exception:
        logger.exception("Impossible to parse educonnect saml response")
        raise exceptions.EduconnectAuthenticationException()

    educonnect_identity = authn_response.get_identity()

    saml_request_id = authn_response.in_response_to

    user_type = educonnect_identity.get(_get_field_oid("7"), [None])[0]
    logout_url = educonnect_identity[_get_field_oid("5")][0]

    if user_type in ["resp1d", "resp2d"]:
        raise exceptions.UserTypeNotStudent(saml_request_id, user_type, logout_url)

    if user_type not in ["eleve1d", "eleve2d"]:
        logger.error("Unknown user type %s", user_type, extra={"saml_request_id": saml_request_id})

    try:
        return models.EduconnectUser(
            birth_date=datetime.strptime(educonnect_identity[_get_field_oid("67")][0], "%Y-%m-%d").date(),
            connection_datetime=_get_connexion_datetime(educonnect_identity),
            educonnect_id=educonnect_identity[_get_field_oid("57")][0],
            first_name=educonnect_identity["givenName"][0],
            ine_hash=educonnect_identity[_get_field_oid("64")][0],
            last_name=educonnect_identity["sn"][0],
            logout_url=logout_url,
            user_type=user_type,
            saml_request_id=saml_request_id,
            school_uai=educonnect_identity.get(_get_field_oid("72"), [None])[0],
            student_level=educonnect_identity.get(_get_field_oid("73"), [None])[0],
        )

    except Exception:
        raise exceptions.ParsingError(educonnect_identity, logout_url)


def _get_field_oid(oid_key: str) -> str:
    return f"urn:oid:1.3.6.1.4.1.20326.10.999.1.{oid_key}"


def build_saml_request_id_key(saml_request_id: str) -> str:
    return f"educonnect-saml-request-{saml_request_id}"


def _get_mocked_user_for_performance_tests(user_id: str) -> models.EduconnectUser:
    user = users_models.User.query.get(int(user_id))
    mocked_saml_request_id = f"saml-request-id_perf-test_{user.id}"
    key = build_saml_request_id_key(mocked_saml_request_id)
    app.redis_client.set(name=key, value=user.id, ex=constants.EDUCONNECT_SAML_REQUEST_ID_TTL)  # type: ignore [attr-defined]

    return users_factories.EduconnectUserFactory(
        birth_date=user.dateOfBirth.date(),
        connection_datetime=datetime.utcnow(),
        educonnect_id=f"educonnect-id_perf-test_{user.id}",
        first_name="".join(random.choice(string.ascii_letters) for _ in range(10)),
        ine_hash=f"inehash_perf-test_{user.id}",
        last_name="".join(random.choice(string.ascii_letters) for _ in range(10)),
        saml_request_id=mocked_saml_request_id,
    )


def _get_connexion_datetime(educonnect_identity: dict) -> datetime | None:
    return (
        datetime.strptime(educonnect_identity[_get_field_oid("6")][0], "%Y-%m-%d %H:%M:%S.%f")
        if _get_field_oid("6") in educonnect_identity
        else None
    )
