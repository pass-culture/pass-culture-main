from flask import Blueprint

from pcapi.routes.native import utils
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


eac_v1 = Blueprint("eac_v1", __name__)
eac_v1.before_request(utils.check_client_version)


EAC_API_KEY_AUTH = "ApiKeyAuth"

security_schemes = {
    EAC_API_KEY_AUTH: {
        "type": "http",
        "scheme": "bearer",
        "description": "Api key shared by Adage and pass Culture",
    }
}

api = ExtendedSpecTree("flask", MODE="strict", before=before_handler, PATH="/", security_schemes=security_schemes)
api.register(eac_v1)
