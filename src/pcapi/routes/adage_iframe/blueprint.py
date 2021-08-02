from flask import Blueprint

from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


adage_iframe = Blueprint("adage_iframe", __name__)


JWT_AUTH = "JWTAuth"

security_schemes = {
    JWT_AUTH: {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
}

api = ExtendedSpecTree(
    "flask",
    title="Pass Culture API accessed through iframe from adage clients",
    MODE="strict",
    before=before_handler,
    PATH="/",
    security_schemes=security_schemes,
)
api.register(adage_iframe)
