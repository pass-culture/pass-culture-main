from flask import Blueprint
from flask_cors.extension import CORS
from spectree import SecurityScheme

from pcapi import settings
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


adage_iframe = Blueprint("adage_iframe", __name__)
CORS(
    adage_iframe,
    origins=settings.CORS_ALLOWED_ORIGINS_ADAGE_IFRAME,
)

JWT_AUTH = "JWTAuth"

SECURITY_SCHEMES = [
    SecurityScheme(name=JWT_AUTH, data={"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}),
]


api = ExtendedSpecTree(
    "flask",
    title="Pass Culture API accessed through iframe from adage clients",
    MODE="strict",
    before=before_handler,
    PATH="/",
    security_schemes=SECURITY_SCHEMES,
    humanize_operation_id=True,
)
api.register(adage_iframe)
