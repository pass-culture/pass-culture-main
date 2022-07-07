from flask import Blueprint
from flask_cors import CORS
from spectree import SecurityScheme

from pcapi import settings
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


backoffice_blueprint = Blueprint("backoffice_blueprint", __name__)
CORS(
    backoffice_blueprint,
    origins=settings.CORS_ALLOWED_ORIGINS_BACKOFFICE,
    supports_credentials=True,
)


BACKOFFICE_AUTH = "backoffice_auth"

SECURITY_SCHEMES = [
    SecurityScheme(
        name=BACKOFFICE_AUTH,
        data={"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
    ),
]


api = ExtendedSpecTree(
    "flask",
    title="pass Culture backoffice API",
    MODE="strict",
    before=before_handler,
    PATH="/",
    security_schemes=SECURITY_SCHEMES,
    humanize_operation_id=True,
    version=1,
)
api.register(backoffice_blueprint)
