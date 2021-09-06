from flask import Blueprint

from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


pro_api_v2 = Blueprint("pro_api_v2", __name__)


API_KEY_AUTH = "ApiKeyAuth"

security_schemes = {
    API_KEY_AUTH: {
        "type": "http",
        "scheme": "bearer",
        "description": "Api key issued by passculture",
    }
}


api = ExtendedSpecTree(
    "flask",
    title="pass Culture public API",
    MODE="strict",
    before=before_handler,
    PATH="/",
    security_schemes=security_schemes,
    version=2,
)
api.register(pro_api_v2)
