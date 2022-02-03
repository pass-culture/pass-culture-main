from flask import Blueprint
from spectree import SecurityScheme
from spectree import SpecTree

from pcapi.routes.native import utils
from pcapi.serialization.utils import before_handler


adage_v1 = Blueprint("adage_v1", __name__)
adage_v1.before_request(utils.check_client_version)


EAC_API_KEY_AUTH = "ApiKeyAuth"

SECURITY_SCHEMES = [
    SecurityScheme(
        name=EAC_API_KEY_AUTH,
        data={"type": "http", "scheme": "bearer", "description": "API key shared by Adage and pass Culture"},
    ),
]


api = SpecTree("flask", MODE="strict", before=before_handler, PATH="/", security_schemes=SECURITY_SCHEMES)
api.register(adage_v1)
