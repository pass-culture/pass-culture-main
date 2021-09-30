import logging
from os import path

from flask import redirect
from saml2 import BINDING_HTTP_POST
from saml2 import xmldsig
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config

from pcapi import settings

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
